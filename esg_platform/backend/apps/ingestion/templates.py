"""
Sample CSV templates for each source type.
These show analysts exactly what columns are expected.
"""

SAP_TEMPLATE = """Plant Code,Material Group,Fuel Type (Material),Quantity (Menge),Unit (ME),Cost Center (Kostenstelle),Posting Date (Buchungsdatum),Vendor Name (Lieferant)
PL001,MG101,Diesel,500,Liters,CC1001,2024-01-15,Shell India
PL001,MG102,Natural Gas,1200,m3,CC1002,2024-01-20,GAIL India
PL002,MG101,Petrol,300,Liters,CC2001,2024-02-01,Indian Oil
PL002,MG103,LPG,150,kg,CC2002,2024-02-10,HP Gas
PL003,MG104,Coal,5000,kg,CC3001,2024-03-01,Coal India
PL001,MG101,Diesel,750,Liters,CC1001,2024-03-15,Shell India
PL002,MG102,Natural Gas,980,m3,CC2001,2024-04-01,GAIL India
PL003,MG101,Diesel,420,Liters,CC3002,2024-04-20,Indian Oil
"""

UTILITY_TEMPLATE = """Meter ID,Billing Start Date,Billing End Date,kWh Usage,Tariff Type,Peak Usage,Off Peak Usage,Facility,Supplier
MTR-001,2024-01-01,2024-01-31,45000,Commercial,28000,17000,Plant A,BESCOM
MTR-002,2024-01-01,2024-01-31,32000,Industrial,20000,12000,Office HQ,TATA Power
MTR-001,2024-02-01,2024-02-29,41000,Commercial,25000,16000,Plant A,BESCOM
MTR-003,2024-02-01,2024-02-29,18500,Residential,11000,7500,Warehouse B,MSEDCL
MTR-002,2024-03-01,2024-03-31,35000,Industrial,22000,13000,Office HQ,TATA Power
MTR-004,2024-03-01,2024-03-31,62000,Industrial,40000,22000,Plant B,BESCOM
"""

TRAVEL_TEMPLATE = """Employee Name,Travel Type,Departure Airport,Arrival Airport,Distance (km),Cabin Class,Hotel Nights,Travel Date,Department
Rahul Sharma,Flight,DEL,BOM,1400,Economy,2,2024-01-10,Sales
Priya Patel,Flight,BOM,LHR,7200,Business,5,2024-01-15,Management
Amit Kumar,Train,,,800,Economy,1,2024-01-20,Engineering
Sunita Rao,Flight,MAA,SIN,3300,Economy,3,2024-02-05,Operations
Vikram Singh,Flight,DEL,DXB,2200,Business,4,2024-02-12,Finance
Neha Gupta,Flight,BOM,JFK,12500,Economy,7,2024-03-01,Sales
Rajesh Nair,Car,,,250,,0,2024-03-10,Engineering
Anita Desai,Flight,HYD,BLR,500,Economy,1,2024-03-15,HR
"""

TEMPLATES = {
    "sap": ("sap_fuel_procurement_template.csv", SAP_TEMPLATE),
    "utility": ("utility_electricity_template.csv", UTILITY_TEMPLATE),
    "travel": ("corporate_travel_template.csv", TRAVEL_TEMPLATE),
}
