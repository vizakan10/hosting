# p
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Replace with your actual MongoDB connection string
MONGO_URI = "mongodb+srv://spello:spello100@spellodb.8zvmy.mongodb.net/?retryWrites=true&w=majority&appName=spelloDB"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["spello_database"]  # Replace with your database name
collection = db["sp1"]  # Replace with your collection name


@app.route("/")
def home():
    return jsonify({"message": "Connected to MongoDB successfully!"})


# Route to store user details in the database
@app.route("/store_user", methods=["POST"])
def store_user():
    data = request.json

    # Validate required fields
    required_fields = ["name", "email", "age", "gender"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "All fields (name, email, age, gender) are required"}), 400

    user = {
        "name": data["name"],
        "email": data["email"],
        "age": data["age"],
        "gender": data["gender"]
    }

    # Insert user data into the database
    result = collection.insert_one(user)
    user["_id"] = str(result.inserted_id)  # Convert ObjectId to string

    return jsonify({"message": "User data stored successfully!", "user": user})



# Route to get all stored users from the database
@app.route("/get_users", methods=["GET"])
def get_users():
    # Retrieve all users from the database
    users = collection.find({}, {"_id": 0})  # Exclude MongoDB's default "_id" field

    user_list = list(users)  # Convert cursor to a list
    return jsonify({"users": user_list})


#get one user based on email
@app.route("/get_user", methods=["GET"])
def get_user():
    email = request.args.get("email")  # Get email from query parameters

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Find user by email, exclude MongoDB "_id" field from response
    user = collection.find_one({"email": email}, {"_id": 0})

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user)


# Route to delete the last inserted user
@app.route("/delete_last_user", methods=["DELETE"])
def delete_last_user():
    # Find the last inserted user
    # Note: This assumes your MongoDB documents have a natural insertion order
    # For a more reliable approach, you might want to add a timestamp field
    last_user = collection.find_one({}, sort=[("_id", -1)])

    if not last_user:
        return jsonify({"error": "No users found in the database"}), 404

    # Delete the last user
    result = collection.delete_one({"_id": last_user["_id"]})

    if result.deleted_count == 1:
        return jsonify({
            "message": "Last user deleted successfully",
            "deleted_user": {
                "name": last_user.get("name"),
                "email": last_user.get("email"),
                "age": last_user.get("age"),
                "gender": last_user.get("gender")
            }
        })
    else:
        return jsonify({"error": "Failed to delete the last user"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
