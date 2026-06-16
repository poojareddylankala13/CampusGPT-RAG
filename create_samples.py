import os
import sys

# Ensure fpdf2 can be used (since the user will run this script, it requires installation)
try:
    from fpdf import FPDF
except ImportError:
    print("Error: 'fpdf2' is not installed. Please run 'pip install fpdf2' first.")
    sys.exit(1)

def create_sample_pdf(filepath, doc_title, sections):
    """Generates a professional looking sample PDF document."""
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(27, 54, 93)  # Navy Blue
    pdf.cell(0, 15, doc_title, ln=True, align="C")
    
    # Subtitle / Line
    pdf.set_draw_color(197, 160, 89)  # Gold
    pdf.set_line_width(1)
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    
    # Sections
    for heading, text in sections:
        # Heading
        pdf.set_font("helvetica", "B", 13)
        pdf.set_text_color(197, 160, 89)  # Gold
        pdf.cell(0, 8, heading, ln=True)
        pdf.ln(2)
        
        # Text body
        pdf.set_font("helvetica", "", 10.5)
        pdf.set_text_color(51, 51, 51)  # Charcoal
        pdf.multi_cell(0, 6, text)
        pdf.ln(6)
        
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    pdf.output(filepath)
    print(f"Created sample document: {os.path.basename(filepath)}")

def generate_all_samples():
    print("Generating sample university documents in 'sample_documents/'...")
    
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_documents')
    
    # 1. Academic Calendar
    calendar_sections = [
        ("1. Introduction", "This document outlines the official academic calendar for the 2026-2027 academic year. All students, faculty, and administrative departments must adhere to these timelines."),
        ("2. Semester Schedules", 
         "Fall Semester 2026: Classes begin on August 24, 2026. The mid-semester examinations will take place from October 12 to October 17, 2026. "
         "Classes resume on October 19. The last day of instruction is December 4, 2026. Final exams are scheduled from December 7 to December 18, 2026. "
         "Winter break begins on December 21, 2026, and ends on January 15, 2027.\n\n"
         "Spring Semester 2027: Classes commence on January 18, 2027. Mid-semester exams will run from March 8 to March 13, 2027. "
         "Spring break will be observed from March 15 to March 20, 2027. Classes end on May 7, 2027. Final semester evaluations will take place from May 10 to May 21, 2027."),
        ("3. Fee Deadlines", 
         "Fall Semester fee payment deadline is August 14, 2026. A late fee of $100 will apply for payments made between August 15 and August 21, 2026. "
         "No registrations will be accepted after instruction begins on August 24.\n\n"
         "Spring Semester fee payment deadline is January 5, 2027. The late fee grace period ends on January 12, 2027."),
        ("4. Important Dates Summary", 
         "- August 14, 2026: Last day for Fall Fee Payment without fine\n"
         "- August 24, 2026: Commencement of Fall Semester Classes\n"
         "- October 12-17, 2026: Fall Mid-Semester Examinations\n"
         "- December 7-18, 2026: Fall Final Examinations\n"
         "- January 18, 2027: Commencement of Spring Semester Classes\n"
         "- March 8-13, 2027: Spring Mid-Semester Examinations\n"
         "- May 10-21, 2027: Spring Final Examinations")
    ]
    create_sample_pdf(os.path.join(target_dir, "Academic_Calendar.pdf"), "Official Academic Calendar (2026-2027)", calendar_sections)
    
    # 2. Student Handbook
    handbook_sections = [
        ("1. Attendance Policy", 
         "The university requires a minimum attendance rate of 75% in each course to be eligible to sit for the final semester examinations. "
         "Students with attendance between 65% and 74% may apply for condonation on medical grounds, supported by valid medical certificates. "
         "Condonation applications must be submitted to the Dean of Academic Affairs within 5 working days of resuming classes. "
         "Any student whose attendance falls below 65% will be automatically barred from examinations and must repeat the course during summer terms."),
        ("2. Grading Scale", 
         "Letter grades are awarded on a 10-point scale as follows:\n"
         "- A+: 10 points (Outstanding)\n"
         "- A: 9 points (Excellent)\n"
         "- B+: 8 points (Very Good)\n"
         "- B: 7 points (Good)\n"
         "- C: 6 points (Satisfactory)\n"
         "- D: 5 points (Pass)\n"
         "- F: 0 points (Fail)\n\n"
         "A minimum Cumulative Grade Point Average (CGPA) of 5.0 is required to remain in good academic standing and for graduation."),
        ("3. Code of Academic Integrity", 
         "Plagiarism, cheating, or any form of unauthorized collaboration is strictly prohibited. First-time offenders will receive a '0' grade on the assessment. "
         "Second-time offenses will be referred to the Disciplinary Board and can result in suspension for one semester. "
         "Repeated integrity violations will lead to permanent expulsion from the university.")
    ]
    create_sample_pdf(os.path.join(target_dir, "Student_Handbook.pdf"), "Student Rules & Regulations Handbook", handbook_sections)
    
    # 3. Placement Guidelines
    placement_sections = [
        ("1. Eligibility Criteria", 
         "To participate in the campus recruitment drive, students must satisfy the following conditions:\n"
         "- Must be in the final year of their undergraduate or postgraduate program.\n"
         "- Must maintain a minimum CGPA of 6.5 with no active backlogs (failed courses) at the time of registrations.\n"
         "- Must have completed the mandatory 8-week summer internship and submitted the internship completion report."),
        ("2. Registration Process", 
         "Students must register on the Central Placement Portal by September 1, 2026. A non-refundable placement registration fee of $50 is applicable. "
         "Registrants must upload their verified resume in PDF format. Resumes cannot exceed one page and must follow the standard university template."),
        ("3. Job Offer Policy (One Student, One Job)", 
         "The university enforces a strict 'One Student, One Job' policy to ensure equal opportunities. Once a student receives an official offer letter from a recruiting company "
         "through the placement cell, they are automatically deregistered from the placement portal and cannot apply for subsequent campus interviews. "
         "Exceptions are made only for 'Dream Offers' (companies offering a package at least 1.5 times the current offer value), subject to prior approval from the Placement Director."),
        ("4. Code of Conduct", 
         "Absence from a scheduled interview without 24-hour advance notice will result in immediate debarment from the entire placement season. "
         "Formal business attire is mandatory for all presentations, tests, and interviews.")
    ]
    create_sample_pdf(os.path.join(target_dir, "Placement_Guidelines.pdf"), "Campus Recruitment & Placement Guidelines", placement_sections)
    
    # 4. Course Syllabus
    syllabus_sections = [
        ("1. Course Details", 
         "Course Code: CS-401\n"
         "Course Title: Introduction to Machine Learning and Data Science\n"
         "Credits: 4 (L: 3, T: 1, P: 0)\n"
         "Prerequisites: Linear Algebra, Probability & Statistics, Python Programming"),
        ("2. Course Objective", 
         "This course introduces core concepts of machine learning, including supervised and unsupervised learning algorithms, "
         "neural networks, model evaluation metrics, and practical applications in python using scikit-learn and tensorflow."),
        ("3. Syllabus Units", 
         "Unit 1: Introduction to Data Preprocessing, Feature Engineering, and Exploratory Data Analysis (EDA) (Weeks 1-3)\n"
         "Unit 2: Supervised Learning - Linear and Logistic Regression, Decision Trees, Random Forests, Support Vector Machines (Weeks 4-7)\n"
         "Unit 3: Unsupervised Learning - K-Means Clustering, Hierarchical Clustering, Principal Component Analysis (PCA) (Weeks 8-10)\n"
         "Unit 4: Introduction to Neural Networks, Backpropagation, and Deep Learning Basics (Weeks 11-13)\n"
         "Unit 5: Model Deployment, Ethics in AI, and Final Project Presentations (Week 14)"),
        ("4. Grade Breakdown", 
         "- Assignments & Quizzes: 20%\n"
         "- Mid-Semester Examination: 30%\n"
         "- Term Project & Lab Assessments: 20%\n"
         "- End-Semester Final Examination: 30%")
    ]
    create_sample_pdf(os.path.join(target_dir, "Course_Syllabus.pdf"), "Course Syllabus: CS-401 Machine Learning", syllabus_sections)
    
    print("All sample documents successfully generated in 'sample_documents/'.")

if __name__ == "__main__":
    generate_all_samples()
