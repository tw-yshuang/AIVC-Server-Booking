# **AIVC-Server-Booking User Manual**

## **`1. Introduction`**  

`AIVC-Server-Booking` aims to let user easily get required computing resouces such as : 
* RAM 
* GPU 
* CPU. 

Simultaneously, this system will efficiently magange server's resources between different users without conflicts. 

Our team use the package, `Docker`, as an important tool to help us distribute resources. Why we use Docker is because it has some characteristic which will be briefly introduce as following article :  

```
With Docker, you can easily package and  deploy your applicatoins. It will collect the infrastructure resouces and applications, which are needs to functions. 

Those evironmental setting are dictated by Docker file which has instructions of how to build the environment. You can costimize it at your will. 

After running the docker file, Docker will create a corresponding container you want and that is the environment you need to run applications.The last and important property is that Docker allows different containers operating simultaneously without affecting to other containers.
```
Because of those properties, when a user want to take advantage of server's computing capability, he no more worry about problems caused by enviromental settings and he can focus on his project.  

Besides integrating Docker, our team try to make this system more usable so that we add additional functions into it. For example:  
1. `User can costimize their required resources.`  
2. `The host maintainer can supervise the usage of server easily.` 

Now, let's start the intructions of AIVC-Server-Booking system.

---
## **`2. Before Booking......`**

Before booking AIVC server, there are somthing you should know ......

1. Ask host maintainer for a new account first. Every account has default limitation of resources. If you want more, you can go to discuss with the host maintainer.

2. You will be forbidden to access server if your used space is out of range. You must sort out your memory space before using server.

3. Every container is removed after it run out of time to release the computing resources being utilized.

4. There are three main directories in each container,  which those directories will be volumed to corresponding ones in host. Let's take a look for their purpose: 
    * `backup_dir` :  Aims to store the configs costimized by the user. Next time, when you want to book server again, you can use configs backed up in backup_dir to build the customization. `未來會增加一些東東`  
    * `work_dir` :  Store user's projects and  personal dataset. Because booking system will automatically delete container with empty work_dir, you should ensure the work_dir has projects in itself to avoid your container from being removed.
    * `dataset_dir` :  It is a read-only folder and supports some common public dataset to every user such as coco dataset. If you have demands about public dataset, you can ask the host maintainer for it. The host maintainer will search it and add it into the directroy. With the management, all users can access the public dataset and no need to download again.


---
## **`3. Booking Usage`**
In this topic, I will instruct the operations of booking step by step including booking method and etral options.  

###  `I. First time to book server`  
Before booking, you can add `-h` option after `booking.py` command. Then you can get an introduction about system.

```zsh
python3 booking.py -h
```

If you are the first time to access this system, you can use the command :  

```zsh
python3 booking.py -id <user_id>
```

Booking system will allow you to create an account. Then you need to key in following informations :  

* *password*
* *forward_port*
* *image*
* *extra_command*  

### 這裡有個問題是，帳號的config是自動生成？還是使用者輸入？以使用者可以輸入為，有問題在改。  

There are some premise you should know :  

*  *`forward_port`* is **`limited within`** <ins>**`10000~11000`**</ins>. Besides, The system will automatically detect which *forward_port* is duplicated.
*  The option, *`image`*, is that if you have customized docker image, you can submit the path of image, which the system will build the container based on your image.
* *`extra_command`* is a arguemnet which will be executed before building container. Customize it to set the environment you want.

### `II. Booking`
Now you have a booking account. Type a command shown as following to start booking :  
*(Adding options will do extral operation to setting the user config. They will be introduced in next topic.)*

```zsh
python3 booking.py <student_id> -<options>
```

Assume that you don't add any options, this system will ask you to input the password and you have two chances to input :

```zsh 
Password:
```

After that, describe how many resouces the container will have :

```zsh
Your Maximum Capability Information: cpus=xx memory=xx gpus=xx
Please enter the capability information 'cpus(float) memory(int) gpus(int)': 
```

As shown above, the first line show the maximum limitations of CPUs, Memories and GPUs. 


介紹功能...
Use command, `booking`, to start book server. There are several CMD options you can use as follow:
|CMD options| Description |
|:--|--|
|"-h" & "--help":||
|"-id" & "--user-id"||
|"-use-opt" & "--use-options"||
|"-ls" & "--list-schedule"||

1. 輸入 學號、密碼、開始時間、結束時間以及所需要的GPU、CPU、Memory的數量完成預約，以上為必填項目。CPU至少 >=1
2. 亦可選填 changed passwd、forward port、image、 extra_command，使用附加功能。
3. Setting the time that you want to use the server.  
4. Setting the server's capability for each container. (CPUs, RAM+SWAP, GPUs)
5. Back up  
6. Set the password and forward port for the container.  
7. 可使用個人的 Docker Image and the initial command  
8. 使用者可透過 CLI 修改 password、forward port、image、extra command
9.

## **`4. Extral Useful Packages Introduction`**
---
After instructions, I recommend you to some packages and commands, which are useful for development.  
*( I will give you a brief introduction. If you want to realize more, you can click the name of package to browse the detail.)*

### `Environment Setting`
Every project have its own required packages. The better way to develop is to build a independent environment for each project. Every project can customize its own *Spec.* based on its requirement.  
Here are some packages which can help you manage your environment : 

### [*pipenv & pyenv*](https://medium.com/ntust-aivc/how-to-install-pyenv-pipenv-in-ubuntu-and-use-multiple-versions-of-python-and-its-suites-3514099a6e05)
With *pyenv*, you can install different versions of python in host and select the certain version which the project need. After that, use *pipenv* to create a clean virtual environment which is the developed environment. You can download the needed packages in virtual environment without messing up the host. 

### [*docker*](https://tw-yshuang.notion.site/Docker-Basic-Introduction-657f817e15a3490d83b84c8a143d6207) 
*docker* can help packages up code and all its dependencies so the application runs quickly and reliably from one computing environment to another.

### `CLI Tools`
### [*git*](https://medium.com/ntust-aivc/introduction-to-git-66473777b9b3)  
*git* is a **distributed version control system**. In this system, Every coworker has a full copy of the project and project histroy. According to the project histroy, you can check who contribute the project and what kind of contribution he added so evey coworker can have an effective communication without barrier. No matter how many people you work with, *git* is a excellent tool to help you realize the whole process of project. It's worth familiarizing.
### [*htop*](https://www.ionos.com/digitalguide/server/tools/htop-the-task-manager-for-linux-mac-os-x-and-bsd/) 
*htop* is a tools that can check the consumptions of computing resources such as **CPU & Memory occupancy**, **Load average**, **total number of tasks and working thread**, and **information of every process**. By means of veiwing the state of computr, you can realize which process cost large amount of resources and kill the one which have bad effects to computer. Checking computing resources help you analyze the efficacy of programs. It's worthwhile to use.
### [*tmux*](https://www.hamvocke.com/blog/a-quick-and-easy-guide-to-tmux/)
***tmux* is a terminal multiplexer.** 
It lets you switch easily between several programs in one terminal. When you detach session, the programs are still running at the background. You can re-access the old programs after retach. Because of this property, you can run programs on background of remote service even though you have detached from that. If you want to access old programs, you can connect to the service with *ssh* and retach the programs by means of *tmux*. That is one of benefits of *tmux*.

*tmux* also can allow you to open multiple *windows* and *panes* in one terminal. Each *pane* contains its own, independtly running shell instance (bash, zsh, ...). You can operate multiple terminal commands and run applications side by side without creating multiple terminals. 

You see that tmux basically offers two big features:
1. Window management in your terminal
2. Session management

There are some commands related to operate *tmux*. You can open the website to search tutorials of *tmux* commands. 

按鍵有更改！！ 說明Prefix 滑鼠 垂直水平分割
列出來怎麼使用

### `Vscode Extensions`
### [Git Graph](https://marketplace.visualstudio.com/items?itemName=mhutchie.git-graph)  
This extention give a GUI of *git*. Let you easily operate functions of *git* without commands. Especially, one of the benefits is that you can check the history of project with visualized graphic. Click the title to browse more detail.

### [Better Comments](https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments)  
This extension supports user-friendly methods to give a comment in code file. Click the title to see a example.

### [Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)
It allows you to use a **container**, **remote machine**, or the **Windows Subsystem for Linux** as a full-featured development environment. You can remotely work on the deployed operating system. When you book a container, you can work on the container with vscode by means of this extensoins.
要在多說一點
## `5. FAQ`
---
Link 到 ../docs/tips/Error 

# `Contributor`

### **110 Postgraduate Researcher** 
* [Yu-Shun Huang](https://github.com/tw-yshuang)
### **109 Undergraduate Researcher**  
* [Tai-Cyuan Ciou](https://github.com/happy91512)
* [Yun-Ching Yeh](https://github.com/ccLLy1n)
* [Jeffrey Chen](https://github.com/Jeffrey0524)
* [Yi-Xiang Yang](https://github.com/Sean053047)








# 撰寫時備註：
yaml 不允許更改，程式是只動到CSV  
users_config.yaml : 使用者資訊，密碼、forward port、image、volume address，使用者可透過 CLI 修改 password、forward port、image、extra command
capability_config.yaml : 設備限制資訊
swap_size can't be setting. It can only be change by host.