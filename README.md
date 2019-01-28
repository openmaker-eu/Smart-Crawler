# Focused Crawling of Online Networked Data

The initial motivation for this work is the task of identifying a community of people that share a common interest and are geographically co-located. 
A slow and somewhat restricted approach for identifying a community is using a referral system. However, such an approach is very labor intensive and hard to automate as it requires personal human to human interactions. In recent years, with the availability of large amounts of publicly available social media data, there is an increasing trend of automatically detecting such communities on social networks. However, several technical challenges still appear in this automation. 

Social networking sites, such as Twitter provide a rich source of dynamic information that is potentially useful for identifying 
communities of people and organizations related to a specific subject. However, even accessing a tiny fraction of this massive data is difficult for third parties due to bandwidth restrictions or cost barriers imposed by commercial or privacy concerns.

## Repo Overview

* twitter-data/ : Contains the anonimized Twitter data that is used for simulations
* docs/ : Contains the references and documentation
    * problem_description.md : Description of the problem
    * model.md : Description of our model
    * references/ :
        * files/  : Contains the files of reference papers
        * literature_survey.md : Abstracts and summaries of references
    * simulation.ipynb : Contains the simulations
* code/ :
    * app/ : Contains the actual code for our app, Smart-Crawler
    * simulator.py : A tool for simulating the Twitter api
    * runner.py : A driver for running the simulations for different policies