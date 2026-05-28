CREATE TABLE agent_students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    cohort VARCHAR(20) NOT NULL,
    gpa NUMERIC(3, 2) DEFAULT 4.00,
    wellbeing_risk VARCHAR(20) DEFAULT 'Low' -- 'Low', 'Medium', 'High'
);

CREATE TABLE agent_courses (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(12) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    credits INT NOT NULL CHECK (credits > 0)
);

CREATE TABLE agent_enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES agent_students(student_id) ON DELETE CASCADE,
    course_id INT REFERENCES agent_courses(course_id) ON DELETE CASCADE,
    enrollment_semester VARCHAR(20) NOT NULL,
    current_grade NUMERIC(5, 2) DEFAULT 100.00,
    status VARCHAR(20) DEFAULT 'Active' -- 'Active', 'Completed', 'Dropped'
);

CREATE TABLE agent_engagement_logs (
    log_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES agent_students(student_id) ON DELETE CASCADE,
    activity_date DATE NOT NULL,
    activity_type VARCHAR(50) NOT NULL, -- 'lms_login', 'forum_contribution', 'assignment_submission'
    duration_minutes INT NOT NULL CHECK (duration_minutes >= 0),
    sentiment_score NUMERIC(3, 2) -- 0.00 (Distressed) to 1.00 (Highly Engaged)
);

CREATE TABLE agent_attendance_logs (
    attendance_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES agent_students(student_id) ON DELETE CASCADE,
    course_id INT REFERENCES agent_courses(course_id) ON DELETE CASCADE,
    class_date DATE NOT NULL,
    status VARCHAR(15) NOT NULL -- 'Present', 'Absent', 'Excused'
);

-- Populate my Friends Students Example Data
INSERT INTO agent_students (name, email, cohort, gpa, wellbeing_risk) VALUES
('Rachel Green', 'rachel.g@academy.edu', '2024-Autumn', 3.85, 'Low'),
('Monica Geller', 'monica.g@academy.edu', '2024-Autumn', 3.98, 'Low'),
('Joey Tribbiani', 'joey.t@academy.edu', '2024-Autumn', 2.10, 'High'),
('Chandler Bing', 'chandler.b@academy.edu', '2025-Spring', 3.40, 'Medium'),
('Ross Geller', 'ross.g@academy.edu', '2024-Autumn', 3.92, 'Low'),
('Phoebe Buffay', 'phoebe.b@academy.edu', '2025-Spring', 2.85, 'Medium'),
('Janice Litman', 'janice.l@academy.edu', '2025-Spring', 1.95, 'High');

-- Populate Courses Example Data
INSERT INTO agent_courses (course_code, course_name, department, credits) VALUES
('COMP1101', 'Introduction to Python Systems', 'Computer Science', 3),
('COMP2201', 'Data Infrastructures and Databases', 'Computer Science', 4),
('EDUC1010', 'Foundations of Modern Pedagogy', 'Education', 3),
('EDUC3022', 'Student Psychology and Wellbeing', 'Education', 3),
('MATH1050', 'Discrete Mathematics & Logic', 'Mathematics', 4);

-- Populate Enrollments Example Data
INSERT INTO agent_enrollments (student_id, course_id, enrollment_semester, current_grade, status) VALUES
(1, 1, '2024-Autumn', 92.50, 'Completed'),
(1, 2, '2025-Spring', 88.00, 'Active'),
(2, 1, '2024-Autumn', 99.00, 'Completed'),
(2, 2, '2025-Spring', 97.50, 'Active'),
(3, 1, '2024-Autumn', 45.00, 'Dropped'),
(3, 3, '2025-Spring', 61.20, 'Active'),
(4, 2, '2025-Spring', 82.00, 'Active'),
(4, 5, '2025-Spring', 74.50, 'Active'),
(5, 5, '2024-Autumn', 95.00, 'Completed'),
(6, 3, '2025-Spring', 78.00, 'Active'),
(7, 1, '2025-Spring', 52.00, 'Active');

-- Populate Engagement Logs Example Data (Simulating Platform metrics over recent days)
INSERT INTO agent_engagement_logs (student_id, activity_date, activity_type, duration_minutes, sentiment_score) VALUES
(1, '2026-05-15', 'lms_login', 45, 0.85),
(1, '2026-05-16', 'assignment_submission', 120, 0.90),
(2, '2026-05-15', 'lms_login', 60, 0.95),
(2, '2026-05-16', 'forum_contribution', 35, 0.90),
(3, '2026-05-10', 'lms_login', 5, 0.20),   -- Here's an example for Joey who had a very brief interaction, highly distressed indicator
(3, '2026-05-14', 'lms_login', 2, 0.15),
(4, '2026-05-15', 'lms_login', 30, 0.60),
(4, '2026-05-16', 'assignment_submission', 85, 0.70),
(6, '2026-05-15', 'forum_contribution', 40, 0.65),
(7, '2026-05-12', 'lms_login', 8, 0.30),   -- Here's an example for Janice: Low log metrics
(7, '2026-05-15', 'lms_login', 4, 0.25);

-- Populate Attendance Logs Example Data
INSERT INTO agent_attendance_logs (student_id, course_id, class_date, status) VALUES
(1, 2, '2026-05-12', 'Present'),
(1, 2, '2026-05-14', 'Present'),
(2, 2, '2026-05-12', 'Present'),
(2, 2, '2026-05-14', 'Present'),
(3, 3, '2026-05-11', 'Absent'),   -- Example Correlation: High risk often correlates with absences
(3, 3, '2026-05-13', 'Absent'),
(4, 2, '2026-05-12', 'Present'),
(4, 2, '2026-05-14', 'Excused'),
(6, 3, '2026-05-11', 'Present'),
(7, 1, '2026-05-12', 'Absent');