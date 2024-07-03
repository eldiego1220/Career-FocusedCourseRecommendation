from flask import Flask, jsonify
import mysql.connector
import os
from dotenv import load_dotenv
from flask import request
import pandas as pd
import sqlalchemy as sa
load_dotenv()

app = Flask(__name__)

# Function to connect to MySQL and execute the query
def query_database(query_number, industry='software', skill_list=['engineering'], course_subject='CS', course_number='411', min_salary = '100000'):
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            sql_query = ""
            # Define your SQL query

            if (query_number == 1):
                sql_query = """
                    SELECT 
                        c.CompanyId,
                        c.Name,
                        AVG(cr.Rating) AS AvgRating
                    FROM 
                        Companies c
                    JOIN 
                        CompanyReviews cr ON c.CompanyId = cr.CompanyId
                    JOIN 
                        CompanyIndustries ci ON c.CompanyId = ci.CompanyId
                    WHERE 
                        ci.Industry LIKE '%""" + str(industry) + """%' 
                    GROUP BY 
                        c.CompanyId, c.Name
                    ORDER BY 
                        AvgRating DESC
                    LIMIT 15;
                """

                sql_query = """
                 CALL GetTopRatedSoftwareCompanies('"""+industry+"""');
                """
            elif (query_number == 2):
                skill_list = skill_list.split(',')
                skill_list_string = "("
                for i, skill in enumerate(skill_list):
                    if i != len(skill_list) - 1:
                        skill_list_string += "'" + skill + "',"
                    else:
                        skill_list_string += "'" + skill + "')"
                sql_query = """
                SELECT jp.JobId, jp.Title AS JobTitle, c.Name AS CompanyName, s.MinSalary
                FROM (
                    SELECT JobId
                    FROM Salaries
                    WHERE MinSalary > """ + min_salary + """ -- Change with desired min
                ) AS SalaryJobs

                JOIN (
                    SELECT js.JobId
                    FROM JobSkills js
                    JOIN Skills s ON js.SkillId = s.SkillId
                    WHERE s.SkillName IN """ + skill_list_string + """ -- Specify the skills you're interested in
                ) AS SkillJobs ON SalaryJobs.JobId = SkillJobs.JobId

                JOIN JobPostings jp ON SalaryJobs.JobId = jp.JobId
                JOIN Companies c ON jp.CompanyId = c.CompanyId
                JOIN Salaries s ON jp.JobId = s.JobId
                ORDER BY s.MinSalary DESC
                LIMIT 15;
                """
            elif (query_number == 3):
                sql_query = """
                SELECT DISTINCT jp.Title AS JobTitle, com.Name AS CompanyName
                FROM JobPostings jp
                JOIN Companies com ON jp.CompanyId = com.CompanyId
                JOIN (
                    SELECT jp.JobId
                    FROM JobPostings jp
                    JOIN Courses c ON jp.Description LIKE CONCAT('%', c.Name, '%')
                    WHERE c.Subject = '""" + course_subject + """' AND c.Number = """ + course_number + """ -- Specify the course subject and number
                    GROUP BY jp.JobId
                ) AS subquery ON jp.JobId = subquery.JobId
                LIMIT 15;
                """

                # sql_query = """
                # CALL GetJobsRelatedToCourse('""" + course_subject + """', """ + course_number + """);
                # """
            elif (query_number == 4):
                sql_query ="""
                SELECT 
                    cr.CompanyId,
                    com.Name AS CompanyName,
                    ROUND(AVG(CASE cr.InterviewDifficulty
                            WHEN 'Easy' THEN 1
                            WHEN 'Medium' THEN 2
                            WHEN 'Difficult' THEN 3
                            ELSE 0
                        END) / COUNT(cr.InterviewDifficulty) * 1.0, 2) AS AverageDifficultyRating,
                    COUNT(cr.InterviewDifficulty) AS NumberOfRatings
                FROM 
                    CompanyReviews cr
                JOIN 
                    CompanyIndustries ci ON cr.CompanyId = ci.CompanyId
                JOIN 
                    Companies com ON cr.CompanyId = com.CompanyId
                WHERE 
                    ci.Industry LIKE '%""" + str(industry) + """%'  -- Specify the industry you're interested in
                GROUP BY 
                    cr.CompanyId, com.Name
                ORDER BY 
                    AverageDifficultyRating DESC
                LIMIT 15;
                """

            # Create a cursor object to execute the query
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query)

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return rows
    except Exception as e:
        print("Error:", e)
        return None

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/query')
def query():
    query_number = request.args.get('query_number')
    industry = request.args.get('industry')
    skill_list = request.args.get('skill_list')
    course_subject = request.args.get('course_subject')
    course_number = request.args.get('course_number')
    min_salary = request.args.get('min_salary')

    query_number = int(query_number)
    
    if query_number == 1:
        result = query_database(query_number, industry)
    elif query_number == 2:
        result = query_database(query_number, min_salary, skill_list)
    elif query_number == 3:
        result = query_database(query_number, course_subject, course_number)
    elif query_number == 4:
        result = query_database(query_number, industry)
    
    print(type(jsonify(result[0])))
    return jsonify(result)

@app.route('/industries')
def industries():
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            sql_query = ""
            # Define your SQL query

            sql_query = """
                SELECT DISTINCT Industry FROM CompanyIndustries;
            """
            # Create a cursor object to execute the query
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query)

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return rows
    except Exception as e:
        print("Error:", e)
        return None

@app.route('/skills')
def skills():
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            sql_query = ""
            # Define your SQL query

            sql_query = """
                SELECT DISTINCT SkillName FROM Skills;
            """
            # Create a cursor object to execute the query
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query)

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return rows
    except Exception as e:
        print("Error:", e)
        return None

@app.route('/search')
def search():
    keyword = request.args.get('keyword')
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            # Define your SQL query

            sql_query = """
                SELECT jp.JobId, C.Name, jp.Title
                FROM JobPostings jp
                LEFT JOIN Companies C on jp.CompanyId = C.CompanyId
                WHERE Title LIKE '%""" + keyword + """%'
                ORDER BY C.Name ASC;
            """
            # Create a cursor object to execute the query
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query)

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return rows
    except Exception as e:
        print("Error:", e)
        return None

@app.route('/nlp')
def nlp():
    job_id = request.args.get('job_id')

    user = os.getenv('DB_USER')
    passwd = os.getenv('DB_PASSWORD')
    db_ip = os.getenv('DB_ADDRESS')
    db_name = 'team_103'

    engine = sa.create_engine(f'mysql://{user}:{passwd}@{db_ip}/{db_name}', echo=False)

    jobs_df = pd.read_sql_table('JobPostings', engine)
    courses_df = pd.read_sql_table('Courses', engine)


    from job_course_matching import get_matching_courses_for_jobs

    jobs_df = jobs_df[jobs_df['JobId'] == job_id]
    courses_df = courses_df

    matching_courses = get_matching_courses_for_jobs(jobs_df, courses_df)

    return matching_courses.to_json(orient='records')

@app.route('/job_lookup')
def job_lookup():
    job_id = request.args.get('job_id')
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            # Define your SQL query

            sql_query = """
                SELECT jp.JobId, C.Name, jp.Title, jp.Description, jp.JobPostingUrl, jp.Location
                FROM JobPostings jp
                LEFT JOIN Companies C on jp.CompanyId = C.CompanyId
                WHERE jp.JobId = """ + job_id + """;
            """
            # Create a cursor object to execute the query
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query)

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return rows
    except Exception as e:
        print("Error:", e)
        return None

@app.route('/course_lookup')
def course_lookup():
    course_subject = request.args.get('course_subject')
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            # Define your SQL query

            sql_query = """
                SELECT CRN, Number, Name FROM Courses WHERE Subject = '""" + course_subject + """' ORDER BY Number;
            """
            # Create a cursor object to execute the query
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query)

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return rows
    except Exception as e:
        print("Error:", e)
        return None
    
@app.route('/company_lookup')
def company_lookup():
    company_name = request.args.get('company_name')
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            # Define your SQL query

            sql_query = """
                SELECT * FROM Companies WHERE Name = '""" + company_name+ """';
            """
            # Create a cursor object to execute the query
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query)

            # Fetch all rows from the result set
            rows = cursor.fetchall()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return rows
    except Exception as e:
        print("Error:", e)
        return None
@app.route('/insert_courses', methods=['POST'])
def insert_courses():
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            
            # Extract data from the form
            CRN = request.form.get('CRN')
            Year = request.form.get('Year')
            Term = request.form.get('Term')
            Subject = request.form.get('Subject')
            Number = request.form.get('Number')
            Name = request.form.get('Name')
            Description = request.form.get('Description')
            CreditHours = request.form.get('CreditHours')
            print(CRN, Year, Term, Subject, Number, Name, Description, CreditHours)

            # Define your SQL query
            sql_query = """
                INSERT INTO Courses (CRN, Year, Term, Subject, Number, Name, Description, CreditHours)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Create a cursor object to execute the query
            cursor = connection.cursor()
            cursor.execute(sql_query, (CRN, Year, Term, Subject, Number, Name, Description, CreditHours))
            connection.commit()  # Commit the transaction

            # Close cursor and connection
            cursor.close()
            connection.close()

            return "Data inserted successfully."
    except Exception as e:
        print("Error:", e)
        return "Failed to insert data."
    
@app.route('/update_courses', methods=['POST'])
def update_courses():
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            
            # Extract data from the form
            CRN = request.form.get('CRN')
            Year = request.form.get('Year')
            Term = request.form.get('Term')
            Subject = request.form.get('Subject')
            Number = request.form.get('Number')
            Name = request.form.get('Name')
            Description = request.form.get('Description')
            CreditHours = request.form.get('CreditHours')

            # Define your SQL query
            sql_query = """
                UPDATE Courses
                SET Year = %s, Term = %s, Subject = %s, Number = %s, Name = %s, Description = %s, CreditHours = %s
                WHERE CRN = %s
            """

            # Create a cursor object to execute the query
            cursor = connection.cursor()
            cursor.execute(sql_query, (Year, Term, Subject, Number, Name, Description, CreditHours, CRN))
            connection.commit()  # Commit the transaction

            # Close cursor and connection
            cursor.close()
            connection.close()

            return "Data updated successfully."
    except Exception as e:
        print("Error:", e)
        return "Failed to update data."
    
@app.route('/delete_courses', methods=['POST'])
def delete_courses():
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            
            # Extract data from the form
            CRN = request.form.get('CRN')

            # Define your SQL query
            sql_query = """
                DELETE FROM Courses
                WHERE CRN = %s
            """

            # Create a cursor object to execute the query
            cursor = connection.cursor()
            cursor.execute(sql_query, (CRN,))
            connection.commit()  # Commit the transaction

            # Close cursor and connection
            cursor.close()
            connection.close()

            return "Data deleted successfully."
    except Exception as e:
        print("Error:", e)
        return "Failed to delete data."

@app.route('/insert_job', methods=['POST'])
def insert_job():
    try:
        # Extract data from the form
        job_id = request.form.get('JobId')
        company_id = request.form.get('CompanyId')
        title = request.form.get('Title')
        description = request.form.get('Description')
        formatted_work_type = request.form.get('FormattedWorkType')
        location = request.form.get('Location')
        remote_allowed = request.form.get('RemoteAllowed')
        job_posting_url = request.form.get('JobPostingUrl')
        sponsored = request.form.get('Sponsored')
        work_type = request.form.get('WorkType')

        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="team_103"
        )

        if connection.is_connected():
            print("Connected to MySQL database")

            # Define your SQL query
            sql_query = """
                INSERT INTO JobPostings 
                (JobId, CompanyId, Title, Description, FormattedWorkType, Location, RemoteAllowed, JobPostingUrl, Sponsored, WorkType)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Create a cursor object to execute the query
            cursor = connection.cursor()
            cursor.execute(sql_query, (job_id, company_id, title, description, formatted_work_type, location, remote_allowed, job_posting_url, sponsored, work_type))
            
            # Commit the transaction
            connection.commit()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return "Job inserted successfully."
    except Exception as e:
        print("Error:", e)
        return "Failed to insert job."

@app.route('/delete_job', methods=['POST'])
def delete_job():
    try:
        # Extract data from the form
        job_id = request.form.get('JobId')

        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="team_103"
        )

        if connection.is_connected():
            print("Connected to MySQL database")

            # Define your SQL query for delete
            sql_query = """
                DELETE FROM JobPostings 
                WHERE JobId = %s
            """

            # Create a cursor object to execute the query
            cursor = connection.cursor()
            cursor.execute(sql_query, (job_id,))

            # Commit the transaction
            connection.commit()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return "Job deleted successfully."
    except Exception as e:
        print("Error:", e)
        return "Failed to delete job."

@app.route('/update_job', methods=['POST'])
def update_job():
    try:
        # Extract data from the form
        job_id = request.form.get('JobId')
        company_id = request.form.get('CompanyId')
        title = request.form.get('Title')
        description = request.form.get('Description')
        formatted_work_type = request.form.get('FormattedWorkType')
        location = request.form.get('Location')
        remote_allowed = request.form.get('RemoteAllowed')
        job_posting_url = request.form.get('JobPostingUrl')
        sponsored = request.form.get('Sponsored')
        work_type = request.form.get('WorkType')

        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="team_103"
        )

        if connection.is_connected():
            print("Connected to MySQL database")

            # Define your SQL query for update
            sql_query = """
                UPDATE JobPostings 
                SET CompanyId = %s, Title = %s, Description = %s, FormattedWorkType = %s,
                    Location = %s, RemoteAllowed = %s, JobPostingUrl = %s, Sponsored = %s, WorkType = %s
                WHERE JobId = %s
            """

            # Create a cursor object to execute the query
            cursor = connection.cursor()
            cursor.execute(sql_query, (company_id, title, description, formatted_work_type,
                                        location, remote_allowed, job_posting_url, sponsored, work_type, job_id))

            # Commit the transaction
            connection.commit()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return "Job updated successfully."
    except Exception as e:
        print("Error:", e)
        return "Failed to update job."

@app.route('/insert_company', methods=['POST'])
def insert_company():
    try:
        # Extract data from the form
        company_id = request.form.get('CompanyId')
        name = request.form.get('Name')
        description = request.form.get('Description')
        company_size = request.form.get('CompanySize')
        state = request.form.get('State')
        country = request.form.get('Country')
        city = request.form.get('City')
        zip_code = request.form.get('ZipCode')
        address = request.form.get('Address')
        url = request.form.get('Url')

        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="team_103"
        )

        if connection.is_connected():
            print("Connected to MySQL database")

            # Define your SQL query for insert
            sql_query = """
                INSERT INTO Companies 
                (CompanyId, Name, Description, CompanySize, State, Country, City, ZipCode, Address, Url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Create a cursor object to execute the query
            cursor = connection.cursor()
            cursor.execute(sql_query, (company_id, name, description, company_size, state, country, city, zip_code, address, url))

            # Commit the transaction
            connection.commit()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return "Company inserted successfully."
    except Exception as e:
        print("Error:", e)
        return "Failed to insert company."

@app.route('/delete_company', methods=['POST'])
def delete_company():
    try:
        # Extract data from the form
        company_id = request.form.get('CompanyId')

        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="team_103"
        )

        if connection.is_connected():
            print("Connected to MySQL database")

            # Define your SQL query for delete
            sql_query = """
                DELETE FROM Companies 
                WHERE CompanyId = %s
            """

            # Create a cursor object to execute the query
            cursor = connection.cursor()
            cursor.execute(sql_query, (company_id,))

            # Commit the transaction
            connection.commit()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return "Company deleted successfully."
    except Exception as e:
        print("Error:", e)
        return "Failed to delete company."
    
@app.route('/update_company', methods=['POST'])
def update_company():
    try:
        # Extract data from the form
        company_id = request.form.get('CompanyId')
        name = request.form.get('Name')
        description = request.form.get('Description')
        company_size = request.form.get('CompanySize')
        state = request.form.get('State')
        country = request.form.get('Country')
        city = request.form.get('City')
        zip_code = request.form.get('ZipCode')
        address = request.form.get('Address')
        url = request.form.get('Url')

        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="team_103"
        )

        if connection.is_connected():
            print("Connected to MySQL database")

            # Define your SQL query for update
            sql_query = """
                UPDATE Companies 
                SET Name = %s, Description = %s, CompanySize = %s, State = %s,
                    Country = %s, City = %s, ZipCode = %s, Address = %s, Url = %s
                WHERE CompanyId = %s
            """

            # Create a cursor object to execute the query
            cursor = connection.cursor()
            cursor.execute(sql_query, (name, description, company_size, state, country, city, zip_code, address, url, company_id))

            # Commit the transaction
            connection.commit()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return "Company updated successfully."
    except Exception as e:
        print("Error:", e)
        return "Failed to update company."

@app.route('/remote_job_transaction')
def remote_job_transaction():
    job_id = request.args.get('job_id')
    try:
        # Establish a connection to your MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"), # Change this to your MySQL password
            database="team_103"
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            # Define your SQL query
            sql_query = "CALL Transaction(%s)"
            # Create a cursor object to execute the query
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query, (job_id,))
            connection.commit()

            # Close cursor and connection
            cursor.close()
            connection.close()

            return jsonify({"message": "Transaction successful."})
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Transaction failed."})




if __name__ == '__main__':
    app.run(debug=True)