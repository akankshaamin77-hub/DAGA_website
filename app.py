
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
CORS(app)


# ==========================================
# MYSQL DATABASE CONNECTION
# ==========================================

def get_db_connection():
    try:
        db_password = os.environ.get("DB_PASSWORD")
        db_host = os.environ.get("DB_HOST", "127.0.0.1")
        db_user = os.environ.get("DB_USER", "root")
        db_name = os.environ.get("DB_NAME", "daga_db")
        db_port = int(os.environ.get("DB_PORT", "3306"))

        if not db_password:
            print("DB_PASSWORD environment variable is missing.")
            return None

        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            connection_timeout=10
        )

        return connection

    except Error as e:
        print("Database connection error:", e)
        return None


# ==========================================
# HOME API
# ==========================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "DAGA Backend is running!",
        "status": "success"
    })


# ==========================================
# DATABASE CONNECTION TEST
# ==========================================

@app.route("/api/test-db", methods=["GET"])
def test_db():

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    connection.close()

    return jsonify({
        "message": "MySQL connected successfully!",
        "database": "daga_db"
    }), 200


# ==========================================
# TOURIST REGISTRATION
# ==========================================

@app.route("/api/tourist/register", methods=["POST"])
def register_tourist():

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")

    if not all([name, email, password]):
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    name = str(name).strip()
    email = str(email).strip().lower()

    if not name or not email or not isinstance(password, str):
        return jsonify({
            "message": "Invalid registration details"
        }), 400

    if len(password) < 8:
        return jsonify({
            "message": "Password must contain at least 8 characters"
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor()

        hashed_password = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO tourists
            (name, email, password, phone)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, hashed_password, phone)
        )

        connection.commit()

        return jsonify({
            "message": "Tourist registered successfully!"
        }), 201

    except IntegrityError:
        connection.rollback()

        return jsonify({
            "message": "This email is already registered"
        }), 409

    except Error as e:
        connection.rollback()
        print("Tourist registration error:", e)

        return jsonify({
            "message": "Tourist registration failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# TOURIST LOGIN
# ==========================================

@app.route("/api/tourist/login", methods=["POST"])
def login_tourist():

    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    email = str(email).strip().lower()

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, password
            FROM tourists
            WHERE email = %s
            """,
            (email,)
        )

        tourist = cursor.fetchone()

        if tourist and check_password_hash(
            tourist["password"], password
        ):

            return jsonify({
                "message": "Login successful!",
                "user_type": "tourist",
                "id": tourist["id"],
                "name": tourist["name"],
                "email": tourist["email"]
            }), 200

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    except Error as e:
        print("Tourist login error:", e)

        return jsonify({
            "message": "Login failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# BUSINESS OWNER REGISTRATION
# ==========================================

@app.route("/api/business/register", methods=["POST"])
def register_business():

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    business_name = data.get("business_name")

    if not all([name, email, password]):
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    name = str(name).strip()
    email = str(email).strip().lower()

    if not name or not email or not isinstance(password, str):
        return jsonify({
            "message": "Invalid registration details"
        }), 400

    if len(password) < 8:
        return jsonify({
            "message": "Password must contain at least 8 characters"
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor()

        hashed_password = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO business_owners
            (name, email, password, phone, business_name)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                name,
                email,
                hashed_password,
                phone,
                business_name
            )
        )

        connection.commit()

        return jsonify({
            "message": "Business owner registered successfully!"
        }), 201

    except IntegrityError:
        connection.rollback()

        return jsonify({
            "message": "This email is already registered"
        }), 409

    except Error as e:
        connection.rollback()
        print("Business registration error:", e)

        return jsonify({
            "message": "Business registration failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# BUSINESS OWNER LOGIN
# ==========================================

@app.route("/api/business/login", methods=["POST"])
def login_business():

    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    email = str(email).strip().lower()

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, password, business_name
            FROM business_owners
            WHERE email = %s
            """,
            (email,)
        )

        business = cursor.fetchone()

        if business and check_password_hash(
            business["password"], password
        ):

            return jsonify({
                "message": "Login successful!",
                "user_type": "business_owner",
                "id": business["id"],
                "name": business["name"],
                "email": business["email"],
                "business_name": business["business_name"]
            }), 200

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    except Error as e:
        print("Business login error:", e)

        return jsonify({
            "message": "Login failed"
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# DESTINATIONS APIs
# ==========================================

# GET ALL DESTINATIONS
@app.route("/api/destinations", methods=["GET"])
def get_destinations():

    connection = get_db_connection()

    if connection is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, location, category, description,
                   activities, best_time, budget, image_url
            FROM destinations
            ORDER BY id DESC
        """)

        destinations = cursor.fetchall()

        return jsonify({
            "status": "success",
            "count": len(destinations),
            "destinations": destinations
        }), 200

    except Error as e:
        print("Get destinations error:", e)
        return jsonify({"message": "Failed to fetch destinations"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# GET SINGLE DESTINATION
@app.route("/api/destinations/<int:destination_id>", methods=["GET"])
def get_destination(destination_id):

    connection = get_db_connection()

    if connection is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, location, category, description,
                   activities, best_time, budget, image_url
            FROM destinations
            WHERE id = %s
        """, (destination_id,))

        destination = cursor.fetchone()

        if destination is None:
            return jsonify({
                "message": "Destination not found"
            }), 404

        return jsonify({
            "status": "success",
            "destination": destination
        }), 200

    except Error as e:
        print("Get destination error:", e)
        return jsonify({"message": "Failed to fetch destination"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# ==========================================
# SERVICES APIs
# ==========================================

# GET ALL APPROVED SERVICES
@app.route("/api/services", methods=["GET"])
def get_services():

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, owner_id, name, category,
                   description, price, unit, status, created_at
            FROM services
            WHERE status = 'Approved'
            ORDER BY id DESC
        """)

        services = cursor.fetchall()

        return jsonify({
            "status": "success",
            "count": len(services),
            "services": services
        }), 200

    except Error as e:
        print("Get services error:", e)

        return jsonify({
            "message": "Failed to fetch services"
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


# GET SINGLE APPROVED SERVICE
@app.route("/api/services/<int:service_id>", methods=["GET"])
def get_service(service_id):

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "message": "Database connection failed"
        }), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, owner_id, name, category,
                   description, price, unit, status, created_at
            FROM services
            WHERE id = %s AND status = 'Approved'
        """, (service_id,))

        service = cursor.fetchone()

        if service is None:
            return jsonify({
                "message": "Service not found"
            }), 404

        return jsonify({
            "status": "success",
            "service": service
        }), 200

    except Error as e:
        print("Get service error:", e)

        return jsonify({
            "message": "Failed to fetch service"
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# BUSINESS PROFILE APIs
# ==========================================

# GET BUSINESS PROFILE

@app.route("/api/business/profile/<int:owner_id>", methods=["GET"]) 
def get_business_profile(owner_id):

    connection = get_db_connection()

    if connection is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, email, phone, business_name, created_at
            FROM business_owners
            WHERE id = %s
        """, (owner_id,))

        owner = cursor.fetchone()

        if owner is None:
            return jsonify({"message": "Business owner not found"}), 404

        return jsonify({
            "status": "success",
            "owner": owner
        }), 200

    except Error as e:
        print("Business profile error:", e)
        return jsonify({"message": "Failed to fetch profile"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# UPDATE BUSINESS PROFILE
@app.route("/api/business/profile/<int:owner_id>", methods=["PUT"])
def update_business_profile(owner_id):

    data = request.get_json(silent=True) or {}

    name = data.get("name")
    business_name = data.get("business_name")
    phone = data.get("phone")

    if not name or not business_name:
        return jsonify({
            "message": "Name and business name are required"
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({"message": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE business_owners
            SET name = %s, business_name = %s, phone = %s
            WHERE id = %s
        """, (name, business_name, phone, owner_id))

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT id FROM business_owners WHERE id = %s",
                (owner_id,)
            )

            if cursor.fetchone() is None:
                return jsonify({
                    "message": "Business owner not found"
                }), 404

        connection.commit()

        return jsonify({
            "status": "success",
            "message": "Business profile updated successfully"
        }), 200

    except Error as e:
        connection.rollback()
        print("Update business profile error:", e)
        return jsonify({"message": "Failed to update profile"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# =========================
# BOOKING APIs
# =========================

@app.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.get_json()

    tourist_id = data.get("tourist_id")
    service_id = data.get("service_id")
    booking_date = data.get("booking_date")
    guests = data.get("guests", 1)

    if not tourist_id or not service_id or not booking_date:
        return jsonify({"message": "Tourist, service and booking date are required."}), 400

    if not isinstance(guests, int) or guests < 1:
        return jsonify({"message": "Guests must be at least 1."}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id, price FROM services WHERE id = %s AND status = 'Approved'",
            (service_id,)
        )
        service = cursor.fetchone()

        if not service:
            return jsonify({"message": "Service not found or not approved."}), 404

        cursor.execute(
            """
            INSERT INTO bookings
            (tourist_id, service_id, tourist_name, tourist_email,
             tourist_phone, booking_date, guests, message, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                tourist_id,
                service_id,
                data.get("tourist_name"),
                data.get("tourist_email"),
                data.get("tourist_phone"),
                booking_date,
                guests,
                data.get("message"),
                service["price"]
            )
        )

        connection.commit()
        booking_id = cursor.lastrowid

        return jsonify({
            "message": "Booking created successfully.",
            "booking_id": booking_id
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/bookings/tourist/<int:tourist_id>", methods=["GET"])
def get_tourist_bookings(tourist_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT b.*, s.name AS service_name,
                   s.category AS service_category,
                   s.unit AS service_unit
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            WHERE b.tourist_id = %s
            ORDER BY b.created_at DESC
            """,
            (tourist_id,)
        )

        bookings = cursor.fetchall()
        return jsonify(bookings), 200

    finally:
        cursor.close()
        connection.close()


@app.route("/api/bookings/business/<int:owner_id>", methods=["GET"])
def get_business_bookings(owner_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT b.*, s.name AS service_name
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            WHERE s.owner_id = %s
            ORDER BY b.created_at DESC
            """,
            (owner_id,)
        )

        bookings = cursor.fetchall()
        return jsonify(bookings), 200

    finally:
        cursor.close()
        connection.close()


@app.route("/api/bookings/<int:booking_id>/status", methods=["PUT"])
def update_booking_status(booking_id):
    data = request.get_json()
    new_status = data.get("status")
    owner_id = data.get("owner_id")

    allowed_statuses = ["Accepted", "Rejected", "Cancelled"]

    if new_status not in allowed_statuses:
        return jsonify({"message": "Invalid booking status."}), 400

    if not owner_id:
        return jsonify({"message": "Owner ID is required."}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT b.id
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            WHERE b.id = %s AND s.owner_id = %s
            """,
            (booking_id, owner_id)
        )

        booking = cursor.fetchone()

        if not booking:
            return jsonify({"message": "Booking not found."}), 404

        cursor.execute(
            "UPDATE bookings SET status = %s WHERE id = %s",
            (new_status, booking_id)
        )

        connection.commit()

        return jsonify({
            "message": "Booking status updated successfully."
        }), 200

    except Exception as e:
        connection.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


# =========================
# REVIEW APIs
# =========================

@app.route("/api/reviews", methods=["POST"])
def create_review():
    data = request.get_json()

    tourist_id = data.get("tourist_id")
    destination_id = data.get("destination_id")
    service_id = data.get("service_id")
    rating = data.get("rating")
    comment = data.get("comment")

    if not tourist_id or rating is None:
        return jsonify({"message": "Tourist ID and rating are required."}), 400

    if destination_id is None and service_id is None:
        return jsonify({
            "message": "A destination ID or service ID is required."
        }), 400

    if destination_id is not None and service_id is not None:
        return jsonify({
            "message": "Review either a destination or a service, not both."
        }), 400

    try:
        rating = int(rating)
    except (ValueError, TypeError):
        return jsonify({"message": "Rating must be a number from 1 to 5."}), 400

    if rating < 1 or rating > 5:
        return jsonify({"message": "Rating must be between 1 and 5."}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        if destination_id is not None:
            cursor.execute(
                "SELECT id FROM destinations WHERE id = %s",
                (destination_id,)
            )
            if not cursor.fetchone():
                return jsonify({"message": "Destination not found."}), 404

        if service_id is not None:
            cursor.execute(
                "SELECT id FROM services WHERE id = %s",
                (service_id,)
            )
            if not cursor.fetchone():
                return jsonify({"message": "Service not found."}), 404

        cursor.execute(
            """
            INSERT INTO reviews
            (tourist_id, destination_id, service_id, rating, comment)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (tourist_id, destination_id, service_id, rating, comment)
        )

        connection.commit()

        return jsonify({
            "message": "Review submitted successfully.",
            "review_id": cursor.lastrowid
        }), 201

    except Exception as e:
        connection.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/reviews/destination/<int:destination_id>", methods=["GET"])
def get_destination_reviews(destination_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT r.id, r.tourist_id, r.rating, r.comment, r.created_at,
                   t.name AS tourist_name
            FROM reviews r
            JOIN tourists t ON r.tourist_id = t.id
            WHERE r.destination_id = %s
            ORDER BY r.created_at DESC
            """,
            (destination_id,)
        )

        reviews = cursor.fetchall()
        return jsonify(reviews), 200

    finally:
        cursor.close()
        connection.close()


@app.route("/api/reviews/service/<int:service_id>", methods=["GET"])
def get_service_reviews(service_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT r.id, r.tourist_id, r.rating, r.comment, r.created_at,
                   t.name AS tourist_name
            FROM reviews r
            JOIN tourists t ON r.tourist_id = t.id
            WHERE r.service_id = %s
            ORDER BY r.created_at DESC
            """,
            (service_id,)
        )

        reviews = cursor.fetchall()
        return jsonify(reviews), 200

    finally:
        cursor.close()
        connection.close()


# =========================
# ADMIN APIs
# =========================

@app.route("/api/admin/register", methods=["POST"])
def admin_register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "All fields are required."}), 400

    hashed_password = generate_password_hash(password)

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO admins (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, hashed_password)
        )

        connection.commit()

        return jsonify({"message": "Admin registered successfully."}), 201

    except mysql.connector.IntegrityError:
        connection.rollback()
        return jsonify({"message": "An admin with this email already exists."}), 409

    except Exception as e:
        connection.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM admins WHERE email = %s",
            (email,)
        )

        admin = cursor.fetchone()

        if admin and check_password_hash(admin["password"], password):
            return jsonify({
                "message": "Admin login successful.",
                "admin": {
                    "id": admin["id"],
                    "name": admin["name"],
                    "email": admin["email"]
                }
            }), 200

        return jsonify({"message": "Invalid email or password."}), 401

    finally:
        cursor.close()
        connection.close()


# =========================
# ADMIN DASHBOARD APIs
# =========================

@app.route("/api/admin/dashboard", methods=["GET"])
def admin_dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM tourists")
        total_tourists = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM business_owners")
        total_owners = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM business_owners
            WHERE status = 'Pending'
        """)
        pending_business_owners = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM services")
        total_services = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM services
            WHERE status = 'Pending'
        """)
        pending_services = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM bookings")
        total_bookings = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM bookings
            WHERE status = 'Pending'
        """)
        pending_bookings = cursor.fetchone()["total"]

        return jsonify({
            "total_tourists": total_tourists,
            "total_business_owners": total_owners,
            "pending_business_owners": pending_business_owners,
            "total_services": total_services,
            "pending_services": pending_services,
            "total_bookings": total_bookings,
            "pending_bookings": pending_bookings
        }), 200

    finally:
        cursor.close()
        connection.close()


@app.route("/api/admin/tourists", methods=["GET"])
def admin_get_tourists():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, name, email, phone
            FROM tourists
            ORDER BY id DESC
            """
        )

        return jsonify(cursor.fetchall()), 200

    finally:
        cursor.close()
        connection.close()



@app.route("/api/admin/business-owners", methods=["GET"])
def admin_get_business_owners():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, name, email, phone, business_name, status, created_at
            FROM business_owners
            ORDER BY id DESC
            """
        )

        return jsonify(cursor.fetchall()), 200

    finally:
        cursor.close()
        connection.close()


@app.route("/api/admin/services", methods=["GET"])
def admin_get_services():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT s.id, s.owner_id, s.name, s.category,
                   s.description, CAST(s.price AS CHAR) AS price,
                   s.unit, s.status, s.created_at,
                   b.business_name
            FROM services s
            JOIN business_owners b ON s.owner_id = b.id
            ORDER BY s.created_at DESC
            """
        )

        return jsonify(cursor.fetchall()), 200

    finally:
        cursor.close()
        connection.close()


@app.route("/api/admin/services/<int:service_id>/status", methods=["PUT"])
def admin_update_service_status(service_id):
    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["Approved", "Rejected"]:
        return jsonify({
            "message": "Status must be Approved or Rejected."
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM services WHERE id = %s",
            (service_id,)
        )

        if not cursor.fetchone():
            return jsonify({"message": "Service not found."}), 404

        cursor.execute(
            "UPDATE services SET status = %s WHERE id = %s",
            (new_status, service_id)
        )

        connection.commit()

        return jsonify({
            "message": "Service status updated successfully.",
            "status": new_status
        }), 200

    except Exception as e:
        connection.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/admin/bookings", methods=["GET"])
def admin_get_bookings():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT b.id, b.tourist_id, b.service_id,
                   b.tourist_name, b.tourist_email,
                   b.tourist_phone, b.booking_date,
                   b.guests, b.message,
                   CAST(b.price AS CHAR) AS price,
                   b.status, b.created_at,
                   s.name AS service_name,
                   s.owner_id
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            ORDER BY b.created_at DESC
            """
        )

        return jsonify(cursor.fetchall()), 200

    finally:
        cursor.close()
        connection.close()


# =========================
# ADMIN BUSINESS APPROVAL API
# =========================

@app.route("/api/admin/business-owners/<int:owner_id>/status", methods=["PUT"])
def admin_update_business_status(owner_id):
    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ["Approved", "Rejected"]:
        return jsonify({
            "message": "Status must be Approved or Rejected."
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id FROM business_owners WHERE id = %s",
            (owner_id,)
        )

        owner = cursor.fetchone()

        if not owner:
            return jsonify({"message": "Business owner not found."}), 404

        cursor.execute(
            """
            UPDATE business_owners
            SET status = %s
            WHERE id = %s
            """,
            (new_status, owner_id)
        )

        connection.commit()

        return jsonify({
            "message": "Business status updated successfully.",
            "owner_id": owner_id,
            "status": new_status
        }), 200

    except Exception as e:
        connection.rollback()
        return jsonify({"message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/business/services", methods=["POST"])
def add_business_service():
    data = request.get_json()

    owner_id = data.get("owner_id")
    name = data.get("name")
    category = data.get("category")
    description = data.get("description")
    price = data.get("price")
    unit = data.get("unit")

    if not all([owner_id, name, category, description, unit]) or price is None:
        return jsonify({"message": "All service details are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO services
            (owner_id, name, category, description, price, unit, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
        """, (owner_id, name, category, description, price, unit))

        connection.commit()

        return jsonify({
            "message": "Service added successfully",
            "service_id": cursor.lastrowid
        }), 201

    except Error as e:
        connection.rollback()
        print("Add service error:", e)
        return jsonify({"message": "Failed to add service"}), 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/business/services/<int:service_id>", methods=["PUT"])
def update_business_service(service_id):
    data = request.get_json()

    owner_id = data.get("owner_id")
    name = data.get("name")
    category = data.get("category")
    description = data.get("description")
    price = data.get("price")
    unit = data.get("unit")

    if not all([owner_id, name, category, description, unit]) or price is None:
        return jsonify({"message": "All service details are required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE services
            SET name = %s, category = %s, description = %s,
                price = %s, unit = %s
            WHERE id = %s AND owner_id = %s
        """, (name, category, description, price, unit, service_id, owner_id))

        if cursor.rowcount == 0:
            return jsonify({"message": "Service not found"}), 404

        connection.commit()

        return jsonify({"message": "Service updated successfully"}), 200

    except Error as e:
        connection.rollback()
        print("Update service error:", e)
        return jsonify({"message": "Failed to update service"}), 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/business/services/<int:service_id>", methods=["DELETE"])
def delete_business_service(service_id):
    data = request.get_json()

    owner_id = data.get("owner_id")

    if not owner_id:
        return jsonify({"message": "Owner ID is required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM services
            WHERE id = %s AND owner_id = %s
        """, (service_id, owner_id))

        if cursor.rowcount == 0:
            return jsonify({"message": "Service not found"}), 404

        connection.commit()

        return jsonify({"message": "Service deleted successfully"}), 200

    except Error as e:
        connection.rollback()
        print("Delete service error:", e)
        return jsonify({"message": "Failed to delete service"}), 500

    finally:
        cursor.close()
        connection.close()


@app.route("/api/business/services/<int:owner_id>", methods=["GET"])
def get_business_owner_services(owner_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, owner_id, name, category, description,
                   price, unit, status, created_at
            FROM services
            WHERE owner_id = %s
            ORDER BY id DESC
        """, (owner_id,))

        services = cursor.fetchall()

        return jsonify({
            "status": "success",
            "services": services
        }), 200

    except Error as e:
        print("Get owner services error:", e)
        return jsonify({
            "message": "Failed to fetch business services"
        }), 500

    finally:
        cursor.close()
        connection.close()


# ==========================================
# RUN FLASK SERVER
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=False
    )
