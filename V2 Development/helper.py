#libraries
from azure.storage.blob import BlobServiceClient
from moviepy.editor import VideoFileClip
import os
from SummaryWriter import summarize_text
from TranscriptGenerator import generate_text
from azure.servicebus import ServiceBusClient
from moviepy.editor import VideoFileClip
import time
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError



import os
import json
from azure.servicebus import ServiceBusClient, ServiceBusMessage

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

# Connection string for Service Bus and the queue name
SERVICE_BUS_CONNECTION_STRING = ""


# def UpdateServiceBus():
# # Initialize ServiceBusClient
#     servicebus_client = ServiceBusClient.from_connection_string(os.getenv("SERVICE_BUS_CONNECTION_STRING"))
#     queue_client = servicebus_client.get_queue_sender(queue_name="video-ingest")
# # Send message to Azure Service Bus queue
#     message = ServiceBusMessage(
#         body=json.dumps({'Key': myblob.name, 'actions': 'transcribe'}),
#         message_id=myblob.name,
#         label='transcribe'
#     )
#     queue_client.send_messages(message)


def UpdateServiceBus(myblob):
    # Initialize ServiceBusClient using a connection string from environment variables
    connection_string = SERVICE_BUS_CONNECTION_STRING

    # Initialize ServiceBusClient and send a message to the queue
    with ServiceBusClient.from_connection_string(connection_string) as servicebus_client:
        with servicebus_client.get_queue_sender(queue_name="video-ingest") as queue_sender:
            try:
                # Create a message to send to the Azure Service Bus queue
                message = ServiceBusMessage(
                    body=json.dumps({'Key': myblob, 'actions': 'transcribe'}),
                    message_id=myblob,
                    label='transcribe'  
                )
                queue_sender.send_messages(message)
                print(f"Message sent successfully for blob: {myblob}")
            except Exception as e:
                print(f"Failed to send message: {e}")
 


def delete_blob():
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_BLOB_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        blobs = container_client.list_blobs()

        for blob in blobs:
            print(f"Deleting: {blob.name}")
            container_client.delete_blob(blob)

def verify_data():
    """
    Verifies if data exists in the specified MongoDB collection.
    """
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)

    # Select the database
    db = client[DATABASE_NAME]

    # Select the collection
    collection = db[CONTAINER_DB_NAME]

    if collection.count_documents({}) == 0:
        print(f"No records found in collection '{CONTAINER_DB_NAME}'.")
        return

    # Retrieve and print all documents in the collection
    print(f"All records in the collection '{CONTAINER_DB_NAME}':")
    records = collection.find()
    for record in records:
        print(record)

def delete_data():
    """
    Verifies if data exists in the specified MongoDB collection.
    """
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)

    # Select the database
    db = client[DATABASE_NAME]

    # Select the collection
    collection = db[CONTAINER_DB_NAME]

    result = collection.delete_many({})

    if collection.count_documents({}) == 0:
        print(f"No records found in collection '{CONTAINER_DB_NAME}'.")
        return

    # Retrieve and print all documents in the collection
    print(f"All records in the collection '{CONTAINER_DB_NAME}':")
    records = collection.find()
    for record in records:
        print(record)


if __name__ == "__main__":
    # delete_blob()
    # delete_data()
    UpdateServiceBus("transcribe-a6b6eb1e-f089-4972-82e5-f8fed887c248-1732075981307")