use alumni;
DROP VIEW IF EXISTS Alumni_Details;
-- Alumni Details
create view Alumni_Details as 
  select Roll_Number, Full_Name, Contact_Number, Branch, Degree, Email, DoB, Year_of_Graduation, Picture 
  from alumni;
GRANT select on Alumni_Details to student;

-- Instructors
create view Instructors as 
  SELECT instructor.*, belongsto.Department_name 
  FROM instructor NATURAL JOIN belongsto 
  order by belongsto.Department_name, instructor.Instructor_ID;
GRANT select on Instructors to student;

-- Departments
GRANT select ON department TO student;

-- Alumni Projects
create view Alumni_Projects as 
  select alumni.Roll_Number, alumni.Full_Name as Student_Name, 
    project_guide.Title as Project_Title, 
    instructor.Instructor_name, 
    projects.Outcome, projects.Duration 
  from project_guide natural join alumni natural join projects natural join instructor 
  order by project_guide.Roll_Number, project_guide.Title;
GRANT select on Alumni_Projects to student;

-- Alumni Achievements
create view Alumni_Achievements as 
  select alumni.Roll_Number, alumni.Full_Name, 
    achievements.Purpose, achievements.Achievement_Date, achievements.Description 
  from alumni natural join achievements 
  order by achievements.Purpose, achievements.Achievement_Date;
GRANT select on Alumni_Achievements to student;

-- Faculty Advisors
create view Faculty_Advisors as 
  SELECT Instructor_Name, Work_email as Email 
  FROM (SELECT DISTINCT Instructor_ID FROM fa) AS f_advisor NATURAL JOIN instructor;
GRANT select on Faculty_Advisors to student;

-- Alumni_Work_Experience
create view Alumni_Work_Experience as 
  select works_in.Roll_Number, alumni.Full_Name as Student_Name, 
    works_in.Company_name, works_in.Role_, works_in.Start_year, works_in.End_year, 
    companies.Company_domain 
  from works_in natural join alumni natural join companies 
  order by works_in.Role_, companies.Company_domain;
GRANT select on Alumni_Work_Experience to student;

-- Alumni_Education
create view Alumni_Education as 
  select alumni.Roll_Number, alumni.Full_Name as Student_Name, 
    studied_in.Full_Name as Institute_Name, studied_in.Degree, studied_in.Discipline, 
    education.Institute_city 
  from studied_in inner join alumni inner join education 
  where studied_in.Full_Name = education.institution_name 
    and studied_in.Discipline = education.Discipline 
    and studied_in.Degree = education.Degree 
    and studied_in.Roll_Number = alumni.Roll_Number
    order by studied_in.Discipline, studied_in.Degree, studied_in.Full_Name;
GRANT select on Alumni_Education to student;

-- Alumni_Extra_Curriculars
create view Alumni_Extra_Curriculars as 
  select alumni.Roll_Number, alumni.Full_Name, 
    extra_curricular.Name_ as Extra_Curricular_Name, extra_curricular.Domain as Extra_Curricular_Domain,
    participates.Role_ as Role, participates.Achievements
  from participates natural join alumni natural join extra_curricular
  order by extra_curricular.Domain, extra_curricular.Name_;
GRANT select on Alumni_Extra_Curriculars to student;
