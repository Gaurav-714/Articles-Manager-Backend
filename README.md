
# Articles Manager Backend API

This repository contains the backend API for the **Articles Management Application**, this **Content Management System (CMS)** is designed to handle comprehensive article and user management. Built using **Django REST Framework**, it integrates advanced **Role-Based Access Control (RBAC)** to enforce security and functionality segregation, ensuring a robust and scalable system.

### API Documentation
   https://documenter.getpostman.com/view/32119544/2sAYBYfVbs

## API Key
   https://api.postman.com/collections/32119544-e5f24412-61e3-4137-bde2-5ec2c6253f37?access_key=PMAT-01JE286BY696WZZ87YB2JD19HF

## Key Features

1. **User Registration and Email Verification**:
   - End users must create an account and verify their email through an OTP sent to their registered email address.
   - After verification, users can request permission to write and publish articles by submitting a message stating their reason.

2. **Authentication and Authorization**:
   - Authentication is mandatory for accessing any part of the system, ensuring secure interactions.
   - JWT-based token authentication is used to manage user sessions.

3. **Password Management**:
   - **Forgot Password**: Users can request an OTP sent to their registered email address to reset their password.
   - **Change Password**: Authenticated users can change their password through a secure endpoint.

4. **Role-Based Access Control (RBAC)**:
   - Central to the application, defining specific actions for Admins, Moderators, and End Users.
   - Custom permission classes ensure that each role can only perform actions they are allowed to.

5. **Article Management**:
   - Create, read, update, and delete articles.
   - Users must be authenticated to read articles.
   - Only the Author of the article, Admins, and Moderators can edit or delete an article.
   - End users must have approval to write and publish articles.

6. **Comment Management**:
   - View, add, edit, or delete comments.
   - Users must be authenticated to read comments.
   - Moderators and Admins have authority over all comments.

7. **Category and Tag Management**:
   - Create, view, update, and delete categories and tags.
   - Moderators and Admins can manage all categories and tags.

8. **Search and Filter Functionality**:
   - **Articles**:
     - Search by title, content, category, and tags.
     - Filter by category, tags, and author's details (email, first_name, last_name).
   - **Comments**:
     - Search by comment content.
   - **Categories and Tags**:
     - Apply filters to view specific categories and tags.

9. **Pagination**:
   - Applied across all item lists, including articles, comments, categories, tags, and user data.

10. **Moderator Functionality**:
    - Moderators can review requests from users seeking permission to publish articles.
    - Authorized to approve or reject the user's request.
    - Full authority to edit or delete articles, comments, categories, and tags.

11. **Admin Features**:
    - Manage users, roles, and permissions.
    - Full access to all resources in the application.
    - Authorized to perform any action over the system.

## Detailed Role-Based Access Control (RBAC)

### Overview
RBAC is the backbone of the system, enforcing strict access policies to ensure secure and logical operation. Each user role has predefined capabilities:

1. **Admin**:
   - Full control over the system, including users, roles, articles, comments, categories, and tags.
   - Create, assign and modify user roles.
2. **Moderator**:
   - Manage and moderate articles, comments, categories, and tags.
   - Approve or reject article publishing requests.
3. **End User**:
   - Register, verify email, and view articles and comments.
   - Submit a request for permission to write articles.
   - Add, edit, or delete their own articles and comments (unless overridden by a moderator).

### Effectiveness and Flexibility
- **Custom Permission Classes**: Ensure role-specific actions are enforced across the system.
- **Dynamic Role Management**: New roles or permissions can be added seamlessly.
- **Secure Access**: Middleware validates roles before accessing endpoints.

### Integration
- Every action, from viewing data to modifying resources, is checked against the user's role and permissions.
- Unauthorized access is denied with clear error responses.

## API Endpoints

### Authentication
- `POST /auth/register/` - Register a new user.
- `POST /auth/login/` - Log in and receive a JWT's access token.
- `POST /auth/verify-otp/` - Verify email using OTP.
- `POST /auth/resend-otp/` - Resend OTP if previous one has expired.

### Password Management
- `POST /auth/forgot-password/` - Request an OTP to reset your password.
- `POST /auth/set-new-password/` - Reset password using the OTP and new password.
- `PUT /auth/change-password/` - Change the password (Authenticated users only).

### Articles
- `POST /content/articles/` - Create an article (Requires Moderator/Admin approval for publishing).
- `GET /content/articles/` - List all articles (with pagination, search, and filters).
- `GET /content/articles/{uid}/` - View an article. (Authenticated user)
- `PUT /content/articles/{uid}/` - Edit an article (Author/Moderator/Admin).
- `DELETE /content/articles/{uid}/` - Delete an article (Author/Moderator/Admin).

### Comments
- `POST /content/comments/` - Add a comment.
- `GET /content/comments/` - List comments on an article (with search and pagination).
- `PUT /content/comments/{uid}/` - Edit a comment (Author/Moderator/Admin).
- `DELETE /content/comments/{uid}/` - Delete a comment (Author/Moderator/Admin).

### Categories and Tags
- `POST /content/categories/` - Create a category (Moderator/Admin).
- `GET /content/categories/` - List categories (with filters and pagination).
- `PUT /content/categories/{id}/` - Edit a category (Moderator/Admin).
- `DELETE /content/categories/{id}/` - Delete a category (Moderator/Admin).
- Same endpoints are available for tags (replace 'categories' with 'tags').

### Moderator Actions
- `GET /manage/view-requests/` - Listout user requests for approval to post content.
- `POST /manage/handle-requests/` - Approve or Reject user's requests.

### Admin Actions
- `POST /manage/create-role/` - Creation of new role by Admin.
- `GET /manage/users/` - Listout users and view details (with filters, search and pagination).
- `GET /manage/users/{uid}/` - View particular user's details.
- `DELETE /manage/users/{uid}/` - Delete particular user.
- `PUT /manage/users/{uid}/` - Update particular user.
- `PATCH /manage/users/{uid}/` - Update particular user partially.

## System Workflow

1. **User Registration**:
   - Users register and verify their email via OTP.
   - Requests to publish articles are submitted for Moderator approval.
2. **Access Control**:
   - Roles and permissions govern all actions.
   - Authentication tokens are required for access.
3. **Moderation**:
   - Moderators review and manage user content.
   - Admins oversee the entire system.

## How to Run Locally

1. Clone the repository and get into the virtual environment:
   ```bash
   git clone https://github.com/Gaurav-714/Articles-Manager-Backend.git
   cd articles-manager-backend
   venv/scripts/activate
   cd core
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the server:
   ```bash
   python manage.py runserver
   ```

5. Access the API at `http://127.0.0.1:8000/`.



