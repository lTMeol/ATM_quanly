from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Cấu hình CORS cho toàn bộ ứng dụng Flask
CORS(app)

# Cấu hình cơ sở dữ liệu
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Tp887799@localhost/ATM_fl'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class ATM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    dia_chi = db.Column(db.String(255), nullable=True)  # Thêm trường địa chỉ
    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id', ondelete='CASCADE'), nullable=False)
    bank = db.relationship('Bank', backref=db.backref('atms', lazy=True))

# Default route
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the ATM Management API!'})

# API Routes

# Thêm ngân hàng mới
@app.route('/api/bank', methods=['POST'])
def add_bank():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Invalid data! Bank name is required!'}), 400
    new_bank = Bank(name=data['name'])
    db.session.add(new_bank)
    db.session.commit()
    return jsonify({'message': 'Bank added successfully!'}), 201

# Lấy danh sách tất cả các ngân hàng
@app.route('/api/bank', methods=['GET'])
def get_banks():
    banks = Bank.query.all()
    return jsonify([{'id': bank.id, 'name': bank.name} for bank in banks])

# Thêm ATM mới
@app.route('/api/atm', methods=['POST'])
def add_atm():
    data = request.json
    if not data or not all(k in data for k in ['name', 'latitude', 'longitude', 'bank_id']):
        return jsonify({'error': 'Invalid data! ATM name, latitude, longitude, and bank_id are required!'}), 400

    # Kiểm tra ngân hàng có tồn tại không
    bank = Bank.query.get(data['bank_id'])
    if not bank:
        return jsonify({'error': 'Bank ID does not exist!'}), 404

    # Thêm ATM vào cơ sở dữ liệu
    new_atm = ATM(
        name=data['name'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        dia_chi=data.get('dia_chi'),  # Thêm địa chỉ nếu có
        bank_id=data['bank_id']
    )
    db.session.add(new_atm)
    db.session.commit()
    return jsonify({'message': 'ATM added successfully!'}), 201

# Lấy danh sách tất cả các ATM
@app.route('/api/atm', methods=['GET'])
def get_atms():
    atms = ATM.query.all()
    return jsonify([{
        'id': atm.id,
        'name': atm.name,
        'latitude': atm.latitude,
        'longitude': atm.longitude,
        'dia_chi': atm.dia_chi,  # Trả về trường địa chỉ
        'bank': {
            'id': atm.bank.id,
            'name': atm.bank.name
        }
    } for atm in atms])

# Lấy thông tin ATM theo ID
@app.route('/api/atm/<int:id>', methods=['GET'])
def get_atm_by_id(id):
    atm = ATM.query.get(id)  # Lấy ATM theo ID từ cơ sở dữ liệu
    if not atm:
        return jsonify({'error': 'ATM not found!'}), 404
    
    return jsonify({
        'id': atm.id,
        'name': atm.name,
        'latitude': atm.latitude,
        'longitude': atm.longitude,
        'dia_chi': atm.dia_chi,  # Trả về trường địa chỉ
        'bank': {
            'id': atm.bank.id,
            'name': atm.bank.name
        }
    }), 200

# Sửa ATM
@app.route('/api/atm/<int:id>', methods=['PUT'])
def update_atm(id):
    data = request.json
    atm = ATM.query.get(id)
    if not atm:
        return jsonify({'error': 'ATM not found!'}), 404

    # Cập nhật các trường thông tin ATM
    atm.name = data.get('name', atm.name)
    atm.latitude = data.get('latitude', atm.latitude)
    atm.longitude = data.get('longitude', atm.longitude)
    atm.dia_chi = data.get('dia_chi', atm.dia_chi)  # Cập nhật địa chỉ nếu có
    atm.bank_id = data.get('bank_id', atm.bank_id)

    db.session.commit()
    return jsonify({'message': 'ATM updated successfully!'}), 200

# Xóa ATM
@app.route('/api/atm/<int:id>', methods=['DELETE'])
def delete_atm(id):
    atm = ATM.query.get(id)
    if not atm:
        return jsonify({'error': 'ATM not found!'}), 404

    db.session.delete(atm)
    db.session.commit()
    return jsonify({'message': 'ATM deleted successfully!'}), 200

# Khởi động ứng dụng
if __name__ == '__main__':
    with app.app_context():  # Create application context
        db.create_all()  # Initialize tables in the database
    app.run(debug=True, host="0.0.0.0", port=5000)
