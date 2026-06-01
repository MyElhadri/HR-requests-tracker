# HR Request Tracker

## Description
A professional Odoo 17/18 module for tracking Human Resources requests. This module centralizes HR requests from employees, enabling a structured workflow and improved visibility for HR managers.

## Features
- **Employee Portal**: Employees can easily submit and track requests.
- **HR Dashboard**: HR managers have a centralized view of all requests.
- **Automated Workflow**: Status tracking (Draft -> Submitted -> In Progress -> Done).
- **Access Rights**: Employees only see their own requests; managers see all.
- **Chatter integration**: Fully integrated with Odoo mail thread and activity mixin.

## Installation
1. Place the `hr_request_tracker` directory in your Odoo `addons` path.
2. Restart the Odoo server.
3. Update the App list in developer mode.
4. Search for "HR Request Tracker" and click Install.

## Testing Guide
1. Create a normal employee user and an HR manager user.
2. Login as the employee.
3. Go to **HR Requests** and click **New**.
4. Fill in the details and save. Note that you cannot submit it until you're ready.
5. Click **Submit**. Observe that you can no longer modify the request.
6. Login as the HR Manager.
7. You should see the request in the Kanban/Tree view.
8. Open the request and click **Start Processing**.
9. Add a response in the **HR Response** tab.
10. Click **Mark Done**.

## Technical details
- Model: `hr.request`
- Security Groups: `Employee (User)` and `HR Manager`.
- Built for Odoo 17 & 18 adhering to modern Odoo standards.
