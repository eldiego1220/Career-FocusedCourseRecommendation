USE team_103;

-- Drop all tables. 
DROP TABLE IF EXISTS Courses, CompanyReviews, JobPostings, Skills, Industries, CompanyIndustries, CompanySpecialities, Companies, EmployeeCounts, Benefits, Salaries, JobIndustries, JobSkills;


CREATE TABLE `Courses` (
  `CRN` int PRIMARY KEY,
  `Year` int,
  `Term` varchar(255),
  `Subject` varchar(255),
  `Number` int,
  `Name` varchar(255),
  `Description` text,
  `CreditHours` varchar(255)
);

CREATE TABLE `CompanyReviews` (
  `ReviewId` int PRIMARY KEY,
  `CompanyId` varchar(255),
  `Rating` real,
  `Reviews` text,
  `Description` text,
  `Happiness` text,
  `CeoApproval` text,
  `CeoCount` text,
  `Ratings` text,
  `Locations` text,
  `Roles` text,
  `Salary` text,
  `InterviewExperience` text,
  `InterviewDifficulty` text,
  `InterviewDuration` text,
  `InterviewCount` text,
  `Revenue` text,
  `Website` text
);

CREATE TABLE `JobPostings` (
  `JobId` varchar(255) PRIMARY KEY,
  `CompanyId` varchar(255),
  `Title` varchar(255),
  `Description` text,
  `FormattedWorkType` varchar(255),
  `Location` varchar(255),
  `Applies` real,
  `OriginalListedTime` real,
  `RemoteAllowed` bool,
  `Views` real,
  `JobPostingUrl` text,
  `ApplicationUrl` text,
  `ApplicationType` varchar(255),
  `Expiry` real,
  `ClosedTime` real,
  `FormattedExperienceLevel` varchar(255),
  `SkillsDesc` text,
  `ListedTime` real,
  `PostingDomain` varchar(255),
  `Sponsored` bool,
  `WorkType` varchar(255),
  `Scraped` int
);

CREATE TABLE `Skills` (
  `SkillId` varchar(255) PRIMARY KEY,
  `SkillName` varchar(255)
);

CREATE TABLE `Industries` (
  `IndustryId` int PRIMARY KEY,
  `IndustryName` varchar(255)
);

CREATE TABLE `CompanyIndustries` (
  `CompanyId` varchar(255),
  `Industry` varchar(255),
  PRIMARY KEY (`CompanyId`, `Industry`)
);

CREATE TABLE `CompanySpecialities` (
  `CompanyId` varchar(255),
  `Speciality` varchar(255),
  PRIMARY KEY (`CompanyId`, `Speciality`)
);

CREATE TABLE `Companies` (
  `CompanyId` varchar(255) PRIMARY KEY,
  `Name` varchar(255),
  `Description` text,
  `CompanySize` real,
  `State` varchar(255),
  `Country` varchar(255),
  `City` varchar(255),
  `ZipCode` varchar(255),
  `Address` varchar(255),
  `Url` varchar(255)
);

CREATE TABLE `EmployeeCounts` (
  `CompanyId` varchar(255) PRIMARY KEY,
  `EmployeeCount` int,
  `FollowerCount` int,
  `TimeRecorded` real
);

CREATE TABLE `Benefits` (
  `JobId` varchar(255),
  `Type` varchar(255),
  `Inferred` bool,
  PRIMARY KEY (`JobId`, `Type`)
);

CREATE TABLE `Salaries` (
  `SalaryId` varchar(255) PRIMARY KEY,
  `JobId` varchar(255),
  `MaxSalary` real,
  `MedSalary` real,
  `MinSalary` real,
  `PayPeriod` varchar(255),
  `Currency` varchar(255),
  `CompensationType` varchar(255)
);

CREATE TABLE `JobIndustries` (
  `JobId` varchar(255),
  `IndustryId` int,
  PRIMARY KEY (`JobId`, `IndustryId`)
);

CREATE TABLE `JobSkills` (
  `JobId` varchar(255),
  `SkillId` varchar(255),
  PRIMARY KEY (`JobId`, `SkillId`)
);

ALTER TABLE `CompanyReviews` ADD FOREIGN KEY (`CompanyId`) REFERENCES `Companies` (`CompanyId`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `JobPostings` ADD FOREIGN KEY (`CompanyId`) REFERENCES `Companies` (`CompanyId`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `CompanyIndustries` ADD FOREIGN KEY (`CompanyId`) REFERENCES `Companies` (`CompanyId`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `CompanySpecialities` ADD FOREIGN KEY (`CompanyId`) REFERENCES `Companies` (`CompanyId`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `EmployeeCounts` ADD FOREIGN KEY (`CompanyId`) REFERENCES `Companies` (`CompanyId`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `Benefits` ADD FOREIGN KEY (`JobId`) REFERENCES `JobPostings` (`JobId`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `Salaries` ADD FOREIGN KEY (`JobId`) REFERENCES `JobPostings` (`JobId`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `JobIndustries` ADD FOREIGN KEY (`JobId`) REFERENCES `JobPostings` (`JobId`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `JobIndustries` ADD FOREIGN KEY (`IndustryId`) REFERENCES `Industries` (`IndustryId`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `JobSkills` ADD FOREIGN KEY (`JobId`) REFERENCES `JobPostings` (`JobId`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE `JobSkills` ADD FOREIGN KEY (`SkillId`) REFERENCES `Skills` (`SkillId`) ON UPDATE CASCADE ON DELETE CASCADE;
