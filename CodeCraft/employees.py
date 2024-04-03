from .models import Employee, EmployeePicture

def get_employee_pictures():
    # Query all employees
    employees = Employee.query.all()
    employee_pictures = {}

    # Iterate through each employee
    for employee in employees:
        # Get the pictures associated with the employee
        pictures = EmployeePicture.query.filter_by(
            employee_id=employee.id
        ).all()
        picture_urls = {"large": None, "medium": None, "thumbnail": None}

        # Extract picture URLs for each size from the pictures
        for picture in pictures:
            if picture.picture_size in picture_urls:
                picture_urls[picture.picture_size] = picture.picture

        # Store the picture URLs for the employee using their ID as the key
        employee_pictures[employee.id] = picture_urls

    return employee_pictures

def get_paginated_employees(page, per_page, search_query):
    employees_query = Employee.query.filter(
            Employee.name.like("%" + search_query + "%")|
            Employee.phone.like("%" + search_query + "%")|
            Employee.age.like("%" + search_query + "%")
        ) if search_query else Employee.query
    
    employees = employees_query.paginate(page=page, per_page=per_page, error_out=False)
    pictures = get_employee_pictures()
    
    paginated_employees = {}
    for employee in employees.items:
        picture = pictures.get(employee.id, {}).get("thumbnail")
        paginated_employees[employee.name] = {
            "id": employee.id,
            "email": employee.email,
            "phone": employee.phone,
            "country": employee.country,
            "age": employee.age,
            "picture": picture,
        }

    return employees, paginated_employees
