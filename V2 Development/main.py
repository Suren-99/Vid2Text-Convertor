#libraries
from azure.storage.blob import BlobServiceClient
from moviepy.editor import VideoFileClip
import os
from SummaryWriter import summarize_text
from TranscriptGenerator import generate_text
from azure.servicebus import ServiceBusClient
from moviepy.editor import VideoFileClip
import time
from pymongo import MongoClient
from pymongo.errors import PyMongoError

 # Azure Blob Storage Configuration
AZURE_BLOB_CONNECTION_STRING = ""
CONTAINER_NAME = "transcribe-video"

# Connection string for Service Bus and the queue name
service_bus_connection_str = ""
queue_name = "video-ingest"

# MongoDB Configuration
MONGODB_URI = ""
DATABASE_NAME = "transcribe-videos"
CONTAINER_DB_NAME = "transcribe-videos-col"

def convert_video_to_mp4(local_file_path):
    file_name, file_extension = os.path.splitext(local_file_path)

    # Convert to mp4 if not already in that format
    if file_extension.lower() != '.mp4':
        mp4_path = file_name + ".mp4"  # Create a new file path with .mp4 extension

        print(f"Converting {local_file_path} to {mp4_path}...")

        try:
            # Open the original video file (e.g., .avi, .mkv)
            with VideoFileClip(local_file_path) as video_clip:
                # Write the video to the new .mp4 file using H.264 codec
                video_clip.write_videofile(mp4_path, codec='libx264')

            print(f"Conversion successful. Saved as {mp4_path}")

            # Update the local_file_path to the new .mp4 file
            local_file_path = mp4_path

        except Exception as e:
            print(f"Error during conversion: {e}")
    else:
        print(f"File is already in .mp4 format: {local_file_path}")

    return local_file_path

def read_message_from_queue():
    # Initialize the Service Bus client
    servicebus_client = ServiceBusClient.from_connection_string(service_bus_connection_str)

    with servicebus_client:
        # Get a receiver for the queue
        receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, max_wait_time=30)
        
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)

        # Select the database
        db = client[DATABASE_NAME]

        # Select the collection
        collection = db[CONTAINER_DB_NAME]

        with receiver:
            for message in receiver:
                document = collection.find_one({"VideoName": message.message_id})

                if document and document.get("status") != "deleted":
                    # Convert the generator to a list and decode the message body
                    message_content = b''.join(list(message.body)).decode('utf-8')

                    # print(f"Received Message: {message_content}")
                    # print(f"Message ID: {message.message_id}")
                    # print(f"Correlation ID: {message.correlation_id}")

                    VIDEO_BLOB_NAME  = message.message_id

                    # Mark the message as complete (deletes it from the queue)
                    receiver.complete_message(message)

                    # **Update the status to 'inprogress' before processing**
                    collection.update_one(
                        {"VideoName": VIDEO_BLOB_NAME},
                        {"$set": {"status": "In Progress"}}
                    )
                    print("Status updated to 'inprogress' in MongoDB.")

                    downloadAndProcess_video(VIDEO_BLOB_NAME)


                    print("Message processed and removed from the queue.")
                else :
                    # Mark the message as complete (deletes it from the queue)
                    receiver.complete_message(message)
                    print("Message removed from the queue.")            

def downloadAndProcess_video(VIDEO_BLOB_NAME):
    try:

        # Initialize Blob Service Client
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        # Generate a unique folder name based on the video filename
        folder_path = os.path.join('uploads', VIDEO_BLOB_NAME)

        # Create the unique folder
        os.makedirs(folder_path, exist_ok=True)

        # Define local download path
        local_file_path = os.path.join(folder_path, VIDEO_BLOB_NAME)

        # Download the video
        print(f"Downloading {VIDEO_BLOB_NAME} from Azure Blob Storage...")
        blob_client = container_client.get_blob_client(VIDEO_BLOB_NAME)
        with open(local_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        print(f"Downloaded video to {local_file_path}")

        container_client.delete_blob(VIDEO_BLOB_NAME)

        local_file_path = convert_video_to_mp4(local_file_path)

        # Generate text from the video
        Text = generate_text(local_file_path,folder_path)

        # Summarize the text
        Summary = summarize_text(Text)

        store_data_in_mongodb(Text, Summary,VIDEO_BLOB_NAME)

    except Exception as e:
        print(f"Error in processing: {e}")
        return None

def store_data_in_mongodb(full_text, summary, VIDEO_BLOB_NAME):
    """
    Convert the transcription and summary to a JSON object and store it in MongoDB.
    """
    try:
        # Initialize MongoDB client
        client = MongoClient(MONGODB_URI)
        database = client[DATABASE_NAME]
        collection = database[CONTAINER_DB_NAME]

        # Prepare the JSON data
        video_data = {
            "VideoName":VIDEO_BLOB_NAME,
            "full_text": full_text,
            "summary": summary,
            "status": "completed"
        }

        # Insert the data into MongoDB
        collection.update_one(
            {"VideoName":VIDEO_BLOB_NAME},  # Filter by video blob name
            {"$set": video_data},  # Update data or insert if not found
            upsert=True  # If the video ID doesn't exist, insert a new record
        )

        print(f"Data successfully stored in MongoDB.")

    except PyMongoError as e:
        print(f"Error storing data in MongoDB: {e}")

def main():
    while True:
        read_message_from_queue()
        time.sleep(2)

if __name__ == "__main__":
    main()
