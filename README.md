# AutoFX - Feedback
ArtFX Discord Server Bot, Custom modules and bot functions

<a name="readme-top"></a>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ArtFX-Support-Crew/AutoFX">
    <img src="images/AFX_bot.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">AutoFX Feedback - Enforce user feedback standards</h3>

  <p align="center">
    <br />
    <a href="https://github.com/ArtFX-Support-Crew/AutoFX"><strong>Documentation »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ArtFX-Support-Crew/AutoFX">Commands</a>
    ·
    <a href="https://github.com/ArtFX-Support-Crew/AutoFX">Report Bug</a>
    ·
    <a href="https://github.com/ArtFX-Support-Crew/AutoFX">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Feedback is a bot which will enforce message standards in forum channels built in Discord.py. While customizable, the specific purpose of the bot is to ensure that meaningful feedback is provided by users replying to another user who has requested feedback on an audio project. 

Where the bot is added, it will enforce post requirements in feedback channels to make sure that new posts meet the requirements. While enabled, initial requirements for feedback posts include a valid audio attachment or link to a music sharing service such as youtube, soundcloud or clypt.it. 

Feedback Requests require Feedback Points, which can be earned by providing feedback for others. To award Feedback Points, messages within forum channel threads are processed to check for meaningful feedback terms and message length. If the message meets the requirements, Feeback Points and Karma Points are awarded to the user replying to the thread. 

A users Feedback Points are reset to zero when a new Feedback Request has made. The required Feedback Points to make a new request is set by default to 1, but this value can be customized by command, as well as most other message requirements enforced by the bot. 

Basic Overview: 


1. Channel check: The bot checks the type of channel where the message is posted. If the channel is a public thread, it will process the messages differently compared to when they are in a text channel. The bot is designed to enforce Feedback standards in forum channels. When the bot is in a text channel, the bot processes messages as commands. 

2. Feedback enforcement: If the channel is a public thread and it is listed as an allowed channel, the bot enforces feedback requirements. It checks if the message meets certain criteria to be considered as a valid feedback request. If not, it deletes the message and informs the author about the issue. If it is valid, it checks if the user has enough feedback points to post the request.

3. Feedback points: Feedback points are a system implemented by this bot to ensure that users are engaging with the community. Users earn feedback points by providing valuable feedback to others. If they don't have enough feedback points, they can't post a feedback request.

4. OpenAI Integration: If enabled in the configuration, the bot uses OpenAI to determine if the feedback response is meaningful.

5. Keyword and character count checks: The bot also checks if the feedback message contains certain required words and meets a minimum character requirement.

6. Awarding points: If a user provides valid feedback (i.e., the feedback contains the required words, meets the character count, and is deemed meaningful by OpenAI), they get feedback points and a "karma point".

9. Command processing: If the message is in a text channel, the bot processes it as a command.



<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* <b><a href="https://discordpy.readthedocs.io/en/stable/">Discord.py</a></b>


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Create 

### Prerequisites

Modules: 
  - discord.py
  - io
  - json
  - math

### Installation

Installing and running the bot:

   
1. Clone the repo and place the files wherever you plan to run the bot
2. Enter your Discord Application API key in config.py
3. Start the bot with main.py

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Usage

1. Configure the bot command prefix in feedback.py and add a text channel ID where the bot will listen for commands. The default prefix is '/'.

Initially the bot will not be responding to commands, an appropriate text channel will have to be configured in feedback_channels.json. You only have to set a text channel to get started and from that point you can change the monitored channels list with commands.  

```
{"forum_channel_ids": [forumchannelid], "text_channel_ids": [textchannelid}
```

After an initial text channel has been set for bot commands. You can use /channel to manage monitored text and forum channels. 

2. Add the forum channel id to feedback_channels.json

```/channel add forum <forumchannelid>```

3. Configure some Feedback Parameters

``` feedback parameters: ```


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3
    - [ ] Nested Feature

See the [open issues](https://github.com/github_username/repo_name/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

ropeadope62 - [@twitter_handle](https://twitter.com/ogslurmsmackenzie)

Project Link: [AutoFX Feedback](https://github.com/ArtFX-Support-Crew/AutoFX/tree/main/feedback)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo_name.svg?style=for-the-badge
[contributors-url]: https://github.com/ArtFX-Support-Crew/AutoFX/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo_name.svg?style=for-the-badge
[forks-url]: https://github.com/ArtFX-Support-Crew/AutoFX/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/repo_name.svg?style=for-the-badge
[stars-url]: https://github.com/ArtFX-Support-Crew/AutoFX/stargazers
[issues-shield]: https://img.shields.io/github/issues/github_username/repo_name.svg?style=for-the-badge
[issues-url]: https://github.com/ArtFX-Support-Crew/AutoFX/issues
[license-shield]: https://img.shields.io/github/license/github_username/repo_name.svg?style=for-the-badge
[license-url]: https://github.com/ArtFX-Support-Crew/AutoFX/blob/master/LICENSE.txt
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
