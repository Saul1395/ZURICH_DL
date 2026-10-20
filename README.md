# ZURICH_DL
Zurich data lead interview

Hi & thank you for reading!

Note: I do apologize for not having tidied up the scripts, sadly I could not
dedicate as much time as I wanted to organize everything

Note 2: If the docker image doesn't work for wathever reazon please use the requirements file to prop up a VM and you should be able to run the pipelines, no problem

Aproach for this case study:
The work done in this case study can be divided in 3 main stages:
 -Data analysis: I divided the analysis in two satges, both contained in the data_analysis.ipynb script
   *Cualitative: Producing insights about general behaivors of the data
   *Modeling focused: Analizing the main hipotesis needed four our models, also searching for relations that migth be useful to exploit
 -Modeling: the cration and testing of the models
  *Data prep: Creating the re-usable pipelines for cleaning and encoding data
  *Modeling: In general I prioritized testing various models instead of spending time optimizations, I belive this is a good first aproach for data you don't know
 -Deployment tasks:
  *pipelines: creating the re-usable pipelines that we would use for deployment
  *model registry: where to store the model, I used ML flow runnig directly on my system but that can be implemented elsewere
  *conteinerization> making the models usable beyond our scope, I created the docker image as a first stage

AI usage:
 In general I tried to limit the use of AI tools as much as possible in the data analysis and modeliing phases, mainly it was used for code refactorin, creating simple functions or creating aestetic configurations, all AI use is disclosed in the comments for both this stages. I mainly used Gemini for this tasks

 AI was used liberally however in the deployment stage, mainly in creating the executables, docker image & other more general requirements. All code was reviewed by me, and adjusted was needed, all steps the Claude took were also provided by me

General assumptions about the data:
-I did not use anything that by definition was directly related with my targets, this includes the risk score external
-I did my test splits in consideration of the insured_id, however I thats the extent of the consideration I gave to that correlation, this is because while checking manually a selection of records I was unable to pice together a coherent way in which those observations where correlated
-For our porpouses the count of claims is uncorrelated to the avg loss

Modeling principle:
 While reviewing the literature I could find about DS in insurance I found that the main metrics for risk are severity and frequency, four our pourpuses this means claim count and avg loss per claim, having said that, I chose to split thefrequency metric in two : probability of having at leat one claim, and, expected number of claims given there were at least one claim
 I've found this aproach to yield better results than modeling everything together

My greatest shames:
 -this migth be because the nature of the data, but I couldn't get any r2 beyond 0.2, most were not even close
 -there is some config off in my docker config that I can't seem to pin down, I belive this is only a problem in my machine but if you are unable to run it, then please try to use a virtual machine with the requirments instead

