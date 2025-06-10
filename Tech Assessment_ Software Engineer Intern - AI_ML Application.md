# AI Engineer Intern \- AI/ML/Gen AI Application 

# Technical Assessment  

Please complete **Tech Assessment 1 and  2** *(optional but encouraged)*. Each assessment builds on top of another.  You will be building a weather app that will take in user-input and then gather data from outside sources (API retrieval) to provide the user with relevant real-time information based on their requests. 

Each assessment will be looking not-only for your technical aptitude but also your ability to think creatively and design innovative solutions. We want you to think like a user who needs to know the weather in their current location or another location of interest they hope to be traveling to. What are some things they should consider that might not be obvious?  
   
The ideal candidate will combine their technical skills to guide the user through their input, validate their input and then store their input and retrieved API data into a database. Then the user should be able to perform CRUD (Create, Read, Update, Delete) operations on this information. 

Please let us know which assessment has been completed. If you only complete the first one, we will still review and consider your application. Ideal candidate will be able to complete parts of  tech assessment 2

# Tech assessment 1: Weather App 

## What We’re Looking For: 

Make a weather app that: 

* Let users enter a location *(any of the following:  Zip Code/Postal Code, GPS Coordinates, Landmarks, Town, City, etc..) * and get the current weather.  You have autonomy to determine how to handle how the user should enter their location   
* Shows the weather clearly, with any details you think are useful. 

To Stand Apart:  

* Add a 5-day forecast   
* Let users see the weather based on their current location.   
* Use icons or images to make the weather info look cool using any design standards.

Again, use whatever technology stack you like\!

Note: Please don’t give static information. Use any  **APIs** to pull real weather information.

NO NEED to make the UI beautiful. Our designer will make your AI product pretty. We just want to see your technical skills. However, if you want to make it nice, feel free to do it. It's nice to have.

# What We Need From You:  See this section below which is the same for Tech Assessment 1 & 2\. 

# Tech assessment 2: Weather App *(Advanced)*

## What We’re Looking For: 

This is a continuation and more advanced section of the weather app development.  This section will focus on persistence with CRUD functionality as well as additional API calls and error handling. The more functionalities are in your code the greater the credibility of your submission. 

Note 1: Users might use many different ways to identify a location *(Zip Code/Postal Code, GPS Coordinates, Landmarks, Town, City, etc..).* You have autonomy to determine how to handle such situations. 

Note 2: Only the CRUD operations via a database are a mandatory requirement, the other sections (API Integration & Data Export are optional but helpful to show aptitude) 

**2.1 CRUD** \- Please choose a database (SQL or noSQL) to have data persistence and incorporate the following functionality. 

* **CREATE** \- Allow user(s) to enter both a location and a date range and output temperate for that location within that date ranges specified. Store all this information into a database.   
  * Validate the date ranges  
  * Validate that the location really exists (or allow fuzzy match for system to determine location)


* **READ** \- Allow users to also be able to read any of the weather information (and anything else stored in the database) they have requested previously (or even what others have entered). \- Row level security is not necessary to segment the data by users.  
    
* **UPDATE** \- Allow users to be able to update any of the weather information stored in the database. (You can pick which data should and shouldn't be updated).    
  * As above have validations so user input is not incoherent or a location is incorrect.


* **DELETE** \- Allow users to be able to delete any of the records in the database.  
  


**2.2 API Integration** \-  \<optional\> Based on the information users provided (above) perform any of the following: 

* Provide Youtube videos of the location user chose  
* Provide Google Map data of the location. *(If location is not specific it is ok to show an approximate point of interest)*  
* Be creative by using any additional API’s.   
  * Here are some free API's for reference \= [https://www.freecodecamp.org/news/public-apis-for-developers/](https://www.freecodecamp.org/news/public-apis-for-developers/)

**2.3 Data Export** \- \<optional\> Allow users to export data from the database into JSON, XML, CSV *(delimited)*, PDF, Markdown output format(s).  \- Feel free to pick whichever (or all) format(s) you prefer for the export. 

# What We Need From You: *(in both Tech Assessment \#1 & \#2)*

* **When**: Please send us your project AS SOON AS POSSIBLE by submitting this [Google form](https://forms.gle/XfM3Xrzpo9sbHr4g8)  no later than 5 days after receiving the assessment. If for special scenarios, you need more time to complete it, let us know.  
    
    
* **How:** Share a link to your **GitHub repo** with the code and a brief README on how to run it and what you did.   
  * IMPORTANT: Public vs. Private repository options  
    * **Set your Github repository “public” and “open-source**”. Or our tech team can’t access and evaluate your code. You can make the repository **“private”** after we finish code evaluation.   
    * Alternatively, you can set your repository to  **private** and then must allow collaboration from Github account \= **PMA-Community**   
      * Allow the ability to **Clone or Download**  
    * Have a **requirements file** show which libraries/packages need to be installed

* Send a short **demo video** of your project \- no fancy editing. Just some recorded screen sharing and 1-2min demo is fine. Share the URL of the demo video in your submission.  *(can be hosted on Google drive or YT, or Vimeo, etc..)* 

* The weather app should include your name and an info button which provide a description of the PM Accelerator ( our LinkedIn page: Product Manager Accelerator has our company’s description).