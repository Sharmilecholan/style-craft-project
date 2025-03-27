from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from extensions import mysql  # Import here
from flask_mail import Mail  # This is required to use the Mail class


auth_bp = Blueprint('auth', __name__)

# Registration Route
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    print("Received Data:", data)  # Debugging line to see received data
    
    # Check if all required fields are present
    if not all(key in data for key in ['name', 'DOB', 'mobile_number', 'email', 'password']):
        print("Missing required fields")
        return jsonify({"message": "Missing required fields"}), 400
    
    try:
        # Hash the password before storing
        hashed_password = generate_password_hash(data['password'])
        
        # Check if email or mobile number already exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s OR mobile_number = %s", 
                    (data['email'], data['mobile_number']))
        existing_user = cur.fetchone()
        
        if existing_user:
            print("Email or Mobile Number already registered")
            return jsonify({"message": "Email or Mobile Number already registered"}), 409
        
        # Insert new user
        cur.execute("""
            INSERT INTO users (name, DOB, mobile_number, email, password_hash, user_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['name'], data['DOB'], data['mobile_number'], data['email'], hashed_password, 'customer'))
        
        mysql.connection.commit()
        cur.close()
        
        print("Registration successful")
        return jsonify({"message": "Registration successful"}), 201
    
    except Exception as e:
        print("Error in Registration:", e)  # Detailed error logging
        return jsonify({"message": "Registration failed", "error": str(e)}), 500
# Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        # Debugging Prints
        print('Input Email:', email)
        print('User from DB:', user)

        # Check if user is None
        if not user:
            print('No user found with this email.')
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Corrected Index for Password Hash
        print('Stored Password Hash:', user[3])  

        # Perform Password Check with Correct Index
        is_password_correct = check_password_hash(user[3], password)
        print('Password Check Result:', is_password_correct)

        if is_password_correct:
            access_token = create_access_token(identity={'id': user[0], 'name': user[1], 'email': user[2]})
            return jsonify({'access_token': access_token}), 200
        else:
            print('Password mismatch')
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        print('Exception:', e)
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
