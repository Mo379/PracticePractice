# PracticePractice
A website for delivering A-level content directly to student, with great features for practicing questions.
# To Do

## General Development process
- Development
	- [ ] Allow all kinds of accounts to be created
	- [ ] Develop the appropriate viewing for every user
	- [ ] Develop the content editing process
	- [ ] Develop the Statistics
	- [ ] Develop the school-teacher-student process
	- [ ] Develop the independent-student process
	- [ ] Develop the payment process
	- [ ] Develop Email templates
	- [ ] 




## Secondary considerations
- [ ] project root
	- [ ] other
	- [x] add .env file
	- [ ] Mount SMTP
- [ ] Base
	- [ ] other
		- [ ] Use a django-javascript workflow
		- [ ] Create Email templates
		- [x] Style the site bootstrap





## APPS
- [ ] Main APP 
	- [ ] templates 
		- [x] index page
		- [x] About page
		- [x] Contact page
		- [x] Sitemap for User page
		- [x] Sitemap for SEO page
		- [x] Terms and conditions page


- [ ] User APP
	- [ ] templates
		- [x] login page
		- [x] Subscriptions page
		- [x] checkout pages
			- [x] Paypal checkout
			- [x] Stripe checkout
	- [ ] models
		- [x] Affiliate balance
		- [x] Affiliate history
		- [ ] User details
			- [ ] Payment details
			- [ ] Regular user details
			- [ ] Choice of level
			- [ ] Choice of subject
			- [ ] Choice of specifications
			- [ ] user groups and group permissions
	- [ ] Features
		- [x] Login
		- [ ] Register
		- [ ] change/Reset password


- [ ] Content APP
	- [ ] templates 
		- [x] Subject's page
		- [x] Questions page
		- [x] Notes page
		- [x] Hub page
		- [x] Paper view page
		- [x] user paper view page
		- [x] user paper print page
	- [ ] Models
		- [x] Specifications
		- [x] Question 
		- [x] Point 
		- [x] Video 
		- [x] User Papers 
		- [x] Question track 
		- [x] Keywords
		- [x] Editing tasks
	- [ ] Utility
		- [x] Make a synchroniser for the data with smart logic
			- [x] Load all questions
			- [x] Load all points
		- [x] Make a CRUD creator bridge| an unordered file creator
			- [x] CRUD specification
			- [x] CRUD subject
			- [x] CRUD moduel
			- [x] CRUD chapter
			- [x] CRUD topic
			- [x] CRUD point
			- [x] CRUD question
	- [ ] site features
		- [ ] Be able to edit json file content directly from the site
			- [ ] Editing Questions
			- [ ] Editing Points
			- [ ] Editing Specs
			- [ ] From json to text and back
		- [ ] Make an editor workflow
			- [ ] Admin to list tasks with payment amounts
			- [ ] Editor to make temporary changes
			- [ ] Editor to submit changes
			- [ ] Admin to be able to check changes
			- [ ] Admin to accept changes
			- [ ] Changes to be applied to content files
			- [ ] Admin to send payment
		- [ ] Make a student workflow
			- [ ] Can view content
			- [ ] Can mark questions
			- [ ] Can watch video
			- [ ] Can see statistics
		- [ ] Paper maker
		- [ ] Question tracking features
			- [ ] Question marking
			- [ ] Elo performance tracking
		- [ ] Video lazy loader
		- [ ] Reporting feature for content improvement
	- [ ] other



## Allowable user actions
- [ ] Group Action map
	- [ ] Everyone
		- [ ] Register
		- [ ] Login
		- [ ] Logout
		- [ ] RecoverPass
		- [ ] ResetPass
		- [ ] Give an experince review
	- [ ] Admins 
		- [ ] Manage editors
		- [ ] Write content
	- [ ] Free user
		- [ ] View Notes
		- [ ] View Pastpaper questions
		- [ ] View pastpapers
		- [ ] Mark questions
		- [ ] View 
	- [ ] Members
		- [ ] View statistics
		- [ ] View model answers
		- [ ] Make UserPaper
		- [ ] View questions by difficulty
		- [ ] View PracticePractice Questions
		- [ ] View Popular specifications
		- [ ] View Chapter progress tracker
		- [ ] View performance tracker
	- [ ] Small Organisations (Tuition centers)
		- [ ] Create class
		- [ ] Create seating plat
		- [ ] Create homework
		- [ ] Release homework answers
	- [ ] Teachers
		- [ ] Create class
		- [ ] Create homework for class
		- [ ] Release homework solutions
		- [ ] Create seating plan for class
		- [ ] Write content
		- [ ] Limited Managing of Editors
	- [ ] Editors
		- [ ] Pickup task
		- [ ] Write content for given task
		- [ ] Submit task
		- [ ] Receive payment
	- [ ] Student
		- [ ] Make payment
		- [ ] Select specifications
		- [ ] Change site appearance
		- [ ] View Notes
		- [ ] Mark Question
		- [ ] Make question paper
		- [ ] View question paper
		- [ ] View Dashboard
		- [ ] View Statistics
	- [ ] Schools
		- [ ] Make payment
		- [ ] Add teachers
		- [ ] Add students
	- [ ] School-students
		- [ ] View Classes
		- [ ] join classes
		- [ ] View homework
		- [ ] submit homework
	- [ ] Affiliates
		- [ ] View history
		- [ ] View balance
		- [ ] Recieve payment






