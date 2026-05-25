# seed_db.py

import sys
from datetime import datetime, timedelta
from app.database.session import SessionLocal, Base, engine
from app.models import model

def seed():
    print("Connecting to database and starting seed process...")
    db = SessionLocal()
    
    # 1. Clear existing data
    print("Clearing existing database tables...")
    db.query(model.OrderDetail).delete()
    db.query(model.Order).delete()
    db.query(model.Customer).delete()
    db.query(model.PurchaseOrderDetail).delete()
    db.query(model.PurchaseOrder).delete()
    db.query(model.Product).delete()
    db.query(model.Supplier).delete()
    db.query(model.User).delete()
    db.commit()

    # 2. Add User
    print("Seeding Users...")
    admin_user = model.User(
        email="admin@inventory.com",
        hashed_password="hashed_password_placeholder" # Simple placeholder for test
    )
    db.add(admin_user)

    # 3. Add Suppliers
    print("Seeding Suppliers...")
    s1 = model.Supplier(
        name="Global Tech Logistics",
        contact_person="Alice Smith",
        email="contact@globaltech.com",
        contact_number="+1 (555) 019-2834",
        category="Electronics"
    )
    s2 = model.Supplier(
        name="EcoPackaging Solutions",
        contact_person="Bob Jones",
        email="info@ecopack.com",
        contact_number="+1 (555) 014-9821",
        category="Packaging"
    )
    s3 = model.Supplier(
        name="Apex Supply Co.",
        contact_person="Charlie Davis",
        email="sales@apexsupply.com",
        contact_number="+1 (555) 012-7634",
        category="Office Supplies"
    )
    db.add_all([s1, s2, s3])
    db.commit()

    # 4. Add Products
    print("Seeding Products...")
    p1 = model.Product(
        name="High-Performance Laptop",
        sku="LAP-HP-001",
        category="Electronics",
        currentStock=45,
        reorderPoint=10,
        supplier=s1.name
    )
    p2 = model.Product(
        name="Wireless Ergonomic Mouse",
        sku="MOU-WL-002",
        category="Electronics",
        currentStock=8,        # Below reorder point!
        reorderPoint=15,
        supplier=s1.name
    )
    p3 = model.Product(
        name="Noise-Cancelling Headphones",
        sku="HDP-NC-003",
        category="Electronics",
        currentStock=12,       # Below reorder point!
        reorderPoint=20,
        supplier=s1.name
    )
    p4 = model.Product(
        name="Biodegradable Shipping Boxes (Medium)",
        sku="BOX-BIO-M",
        category="Packaging",
        currentStock=150,
        reorderPoint=50,
        supplier=s2.name
    )
    p5 = model.Product(
        name="Premium Dual-Tip Markers (Set of 24)",
        sku="MRK-SET-24",
        category="Office Supplies",
        currentStock=3,        # Below reorder point!
        reorderPoint=10,
        supplier=s3.name
    )
    p6 = model.Product(
        name="Heavy Duty Tape Dispenser",
        sku="DIS-HD-99",
        category="Office Supplies",
        currentStock=25,
        reorderPoint=5,
        supplier=s3.name
    )
    db.add_all([p1, p2, p3, p4, p5, p6])
    db.commit()

    # 5. Add Customers
    print("Seeding Customers...")
    c1 = model.Customer(
        name="Acme Corporation",
        email="procurement@acme.com",
        phone="+1 (555) 111-2222",
        address="123 Industrial Parkway, Suite A, Detroit, MI"
    )
    c2 = model.Customer(
        name="Jane Wilson",
        email="jane.wilson@gmail.com",
        phone="+1 (555) 333-4444",
        address="789 Residential Road, Apartment 4B, Boston, MA"
    )
    c3 = model.Customer(
        name="TechStart Inc.",
        email="hello@techstart.io",
        phone="+1 (555) 555-6666",
        address="456 Innovation Blvd, Tech City, CA"
    )
    db.add_all([c1, c2, c3])
    db.commit()

    # 6. Add Orders and OrderDetails
    print("Seeding Orders and OrderDetails...")
    now = datetime.now()
    
    # Order 1: Delivered (3 days ago)
    o1 = model.Order(
        customer_id=c1.id,
        order_date=now - timedelta(days=3),
        status="Delivered"
    )
    db.add(o1)
    db.commit()
    od1 = model.OrderDetail(order_id=o1.id, product_id=p1.id, quantity=3, price_at_sale=1200.0)
    od2 = model.OrderDetail(order_id=o1.id, product_id=p2.id, quantity=5, price_at_sale=49.99)
    db.add_all([od1, od2])

    # Order 2: Shipped (1 day ago)
    o2 = model.Order(
        customer_id=c2.id,
        order_date=now - timedelta(days=1),
        status="Shipped"
    )
    db.add(o2)
    db.commit()
    od3 = model.OrderDetail(order_id=o2.id, product_id=p3.id, quantity=2, price_at_sale=199.99)
    db.add(od3)

    # Order 3: Pending (Today!)
    o3 = model.Order(
        customer_id=c3.id,
        order_date=now,
        status="Pending"
    )
    db.add(o3)
    db.commit()
    od4 = model.OrderDetail(order_id=o3.id, product_id=p1.id, quantity=1, price_at_sale=1200.0)
    od5 = model.OrderDetail(order_id=o3.id, product_id=p4.id, quantity=10, price_at_sale=2.5)
    db.add_all([od4, od5])

    # Order 4: Old Pending Order (to trigger old pending order Priority Task!)
    o4 = model.Order(
        customer_id=c1.id,
        order_date=now - timedelta(days=2),
        status="Pending"
    )
    db.add(o4)
    db.commit()
    od6 = model.OrderDetail(order_id=o4.id, product_id=p5.id, quantity=2, price_at_sale=19.99)
    db.add(od6)

    # 7. Add PurchaseOrders (Supplier shipments)
    # PO 1: Pending (to trigger Late Shipment Priority Task!)
    po1 = model.PurchaseOrder(
        supplier_id=s1.id,
        order_date=now - timedelta(days=5),
        status="Pending"
    )
    db.add(po1)
    db.commit()
    pod1 = model.PurchaseOrderDetail(purchase_order_id=po1.id, product_id=p2.id, quantity=50)
    db.add(pod1)

    db.commit()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed()
