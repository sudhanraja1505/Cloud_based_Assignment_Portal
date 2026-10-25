# Cloud-Based Student Assignment Submission Portal

## 1. Project Overview

The Cloud-Based Student Assignment Submission Portal is a web application designed to simplify the process of creating, submitting, and managing academic assignments. It provides a common platform for students and teachers to manage assignments online.

Students can view assignments, check deadlines, and upload their completed work. Teachers can create assignments, review student submissions, and download submitted files. Cloud services are used to store assignment information and submission files securely and make them accessible online.

## 2. Objectives

- To provide an online platform for assignment submission.
- To reduce paperwork and manual assignment management.
- To allow teachers to create assignments and set deadlines.
- To enable students to submit assignments from anywhere.
- To store assignment details and files using cloud services.
- To improve communication and assignment management between students and teachers.

## 3. Features

### Student Module
- Student registration and login.
- View available assignments.
- Check assignment deadlines.
- Upload completed assignments.
- View submission status.

### Teacher Module
- Teacher login and dashboard.
- Create and manage assignments.
- Set assignment deadlines and descriptions.
- View student submissions.
- Download submitted assignment files.

### Cloud Features
- Cloud-based storage for assignment files.
- Centralized storage of assignment and submission details.
- Online access from different devices.
- Reduced dependency on local computer storage.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Backend web framework |
| HTML5 | Web page structure |
| CSS3 | User interface styling |
| Firebase Authentication | User authentication |
| Cloud Firestore | Assignment and submission data |
| Firebase Storage | Assignment file storage |

## 5. System Requirements

### Hardware Requirements
- Processor: Intel Core i3 or above
- RAM: Minimum 4 GB
- Storage: Minimum 1 GB of free space
- Internet connection

### Software Requirements
- Windows, Linux, or macOS
- Python 3.10 or above
- Visual Studio Code or another code editor
- Web browser
- Firebase account and project

## 6. System Architecture

The application follows a client-server architecture.

1. The student or teacher accesses the application through a web browser.
2. The Flask backend handles application requests.
3. Firebase Authentication manages user authentication.
4. Cloud Firestore stores assignment details and submission metadata.
5. Firebase Storage stores uploaded assignment files.
6. The application retrieves the relevant information and displays it to the user.

## 7. Project Structure

```text
cloud-assignment-portal/
│
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── student_dashboard.html
│   └── teacher_dashboard.html
│
├── static/
│   └── style.css
│
└── config/
    └── firebase_setup.py
```

*Note: This is a suggested project structure. Update it to match the actual files in your implementation.*

## 8. Installation and Setup

### Step 1: Clone or Download the Project

Download the project source code and open its folder in Visual Studio Code.

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Firebase

1. Create a project in the Firebase Console.
2. Enable the required authentication method.
3. Create a Cloud Firestore database.
4. Configure Firebase Storage if file uploads are required.
5. Configure the Firebase credentials securely.
6. Apply appropriate security rules for users and uploaded files.

Firebase configuration must match the authentication and database approach used by the application.

### Step 5: Run the Application

```bash
python app.py
```

Open the local URL displayed in the terminal in your web browser. For a typical Flask development server, this is:

`http://127.0.0.1:5000`

## 9. Working Procedure

1. A user registers or logs in.
2. A teacher creates an assignment with a description and deadline.
3. The assignment is stored in the cloud database.
4. Students view the available assignments.
5. Students upload their completed assignment files.
6. Submission details are saved in the database, and files are stored in cloud storage.
7. Teachers view and download the submitted assignments.
   
   <img width="1867" height="882" alt="Screenshot 2026-10-25 212349" src="https://github.com/user-attachments/assets/4ff91497-6ef7-4911-b6d1-23162a242384" />


## 10. Advantages

- Easy and convenient assignment submission.
- Reduces paper usage.
- Provides centralized assignment management.
- Supports remote access through the internet.
- Simplifies file sharing between students and teachers.
- Can be expanded to support additional users and features.

## 11. Future Enhancements

- Assignment grading and feedback.
- Email notifications for deadlines.
- Plagiarism detection.
- Late-submission tracking.
- Student performance reports.
- Mobile-friendly interface.
- Integration with learning management systems.

## 12. Conclusion

The Cloud-Based Student Assignment Submission Portal provides an efficient solution for managing academic assignments online. By combining a Flask web application with cloud authentication, database services, and file storage, the system simplifies assignment creation, submission, and review. The project demonstrates the practical application of cloud computing in educational institutions and can be extended with additional academic management features.

## 13. Security Considerations

- Use secure authentication and authorization.
- Restrict assignment creation to authorized teachers.
- Ensure students can access only permitted resources.
- Validate uploaded file types and sizes.
- Configure appropriate cloud database and storage security rules.
- Never publish private keys, passwords, or service account credentials in the source code or public repository.
