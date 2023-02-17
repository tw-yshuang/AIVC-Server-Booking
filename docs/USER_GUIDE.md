# **AIVC-Server-Booking User Manual**

## **`1. Introduction`**  

`AIVC-Server-Booking` aims to let user easily get required computing resouces such as : 
* RAM 
* GPU 
* CPU 
* HDD.

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
## **`2. Before booking......`**

Before booking AIVC server, there are somthing you should know ......

1. Ask host maintainer for a new account first. Every account has default limitation of resources. If you want more, you can go to discuss with the host maintainer.

2. You will be forbidden to access server if your used space is out of range. You must sort out your memory space before using server.

3. Every container is deleted after it run out of time to release the computing resources being utilized.

4. There are three main directories in each container,  which those directories will be volumed to corresponding ones in host. Let's take a look for their purpose: 
    * `backup_dir` :  Aims to store the configs costimized by the user. Next time, when you want to book server again, you can use configs backed up in backup_dir to build the customization.  
    * `work_dir` :  Store user's projects and  personal dataset. Because booking system will automatically delete container with empty work_dir, you should ensure the work_dir has projects in itself to avoid your container from being removed.
    * `data_dir` :  It is a read-only folder and supports some common public dataset to every user such as coco dataset. If you have demands about public dataset, you can ask the host maintainer for it. The host maintainer will search it and add it into the directroy. With the management, all users can access the public dataset and no need to download again.


---
## **`3. Booking Usage`**
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
## 

## `4. Extral Usful Packages Introduction`
---

介紹一些酷酷有趣的功能

### **Environment setting**
### pipenv & pyenv (link)
### docker (link)
### **Useful package** 
### htop (Intro)
### tmux (link)
### git  (link)
### docker (link)

### **Vscode extensions**



## `5. FAQ`
---
Link 到 ../docs/tips/Error 

# `Contributor`


### 109 Undergraduate Researcher  
Yi-Xiang Yang: 

# 撰寫時備註：
yaml 不允許更改，程式是只動到CSV  
users_config.yaml : 使用者資訊，密碼、forward port、image、volume address，使用者可透過 CLI 修改 password、forward port、image、extra command
capability_config.yaml : 設備限制資訊
swap_size can't be setting. It can only be change by host.