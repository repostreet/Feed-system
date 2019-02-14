Create a folder with any name and navigate inside it.

1. Installing python 3.7 -

   sudo apt-get update
   sudo apt-get install software-properties-common

   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt-get update
   sudo apt-get install python3.7

2. Creating virtualenv -

   # If virtualenvwrapper is installed - 
   mkvirtualenv --python=python3.7 <env_name>

   # else
   virtualenv -p /usr/bin/python3.7 <env_name>
   source env_name/bin/activate

3. Pulling the repo into your system -

   git clone https://gitlab.com/samimsk007/feedapp.git

4. Installing the dependencies - 

   cd feedapp
   pip freeze -r requirements.txt

5. Database migrations - 

   python manage.py makemigrations
   python manage.py migrate

6. Running the app

   1. python manage.py runserver
   2. Open a new terminal and navigate inside
      the cloned repo i,e feedapp and activate
      the virtualenv. Then navigate inside socket_server
      folder and run the follwing cmd - 
      python server.py 

Best regards, 
samim


   
      
    


          
