<h2 align="center">
    ─「 𝐒ɪᴍᴘʟᴇ 𝘅 𝐌ᴜsɪᴄ 」─
</h2>

[![Typing SVG](https://readme-typing-svg.herokuapp.com/?lines=ㅤ+𝚆𝙴𝙻𝙲𝙾𝙼𝙴+𝚃𝙾+𝚂𝙸𝙼𝙿𝙻𝙴+𝙼𝚄𝚂𝙸𝙲+𝚁𝙴𝙿𝙾+;ㅤ+𝚃𝙷𝙸𝗦+𝙸𝗦+𝙰+𝙰𝙳𝚅𝙰𝙽𝙲𝙴+𝙼𝚄𝚂𝙸𝙲+𝙱𝙾𝚃;𝙿𝙾𝚆𝙴𝚁𝙴𝙳+𝙱𝚈+☞+𝗧𝗛𝗘+𝗧𝗘𝗔𝗠+𝗦𝗜𝗠𝗣𝗟𝗘)](https://github.com/Simple-Boy-1k/SIMPLE_MUSIC)

<p align="center">
  <img src="https://files.catbox.moe/z1h6ow.jpg">
</p>

![Typing SVG](https://readme-typing-svg.herokuapp.com/?lines=𝗙𝗢𝗥𝗞+𝗧𝗛𝗜𝗦+𝗥𝗘𝗣𝗢+𝗕𝗘𝗙𝗢𝗥𝗘+𝗗𝗘𝗣𝗟𝗢𝗬)

## 🍁 About This Bot :

<p align='center'>
This repo will use to deploy for music playing bot of telegram
</p>

## ♢ How to make your own :

#### ♢ Click on This Drop-down and get more details

<br>

<details>
<summary><b>Deploy on Heroku:</b></summary>

1. Fork This Repo  
2. Click on the button to Deploy and follow steps  

<h4> So Follow Above Steps 👆 and then deploy other wise bot won't work</h4>

Press the below button to Fast deploy on Heroku/Railway  
Either you could locally host or deploy on [Heroku](https://heroku.com)

### 💜 Heroku

<p align="center">
<a href="https://dashboard.heroku.com/new?template=https://github.com/Simple-Boy-1k/SIMPLE_MUSIC">
<img src="https://www.herokucdn.com/deploy/button.svg">
</a>
</p>

<br>

then goto the <a href="#mandatory-vars">variables tab</a> for more info on setting up environmental variables.

</details>

<details>
<summary><b>Features:</b></summary>

<p>

🚀Features<p>  
💥Superfast⚡️ download and stream links.<br>  
💥No ads in playing songs.<br>  
💥Superfast interface.<br>  
💥Updates channel Support.<br>  
💥Mongodb database support for broadcasting.<br>  
💥User Friendly Interface.<br>  
💥Ping check.<br>  
💥Kickme and Video Chat Notifier are Available.<br>  
💥Real time CPU , RAM , Internet usage. <br>  
💥All unwanted code removed. <br>  
💥A lot more tired of writing check out by deploying it.  

</details>

<details>
<summary><b>Host it on VPS Locally :</b></summary>

```py
sudo apt-get install python3-pip ffmpeg -y
sudo apt-get install python3-pip -y
sudo pip3 install -U pip

curl -fssL https://deb.nodesource.com/setup_19.x | sudo -E bash -
sudo apt-get install nodejs -y
npm i -g npm

git clone https://github.com/Simple-Boy-1k/SIMPLE_MUSIC
cd SIMPLE_MUSIC

pip3 install -U -r requirements.txt

bash setup

sudo apt install tmux

tmux kill-session
tmux

bash start

Ctrl+b then d
```

and to stop the whole bot,  
do <kbd>CTRL</kbd> + <kbd>C</kbd>

### Setting up things

If you're on Heroku, just add these in the Environmental Variables  
or if you're Locally hosting, create a file named `sample.env` in the root directory and add all the variables there.

Example of `sample.env` file:

```env
API_ID=
API_HASH=
BOT_TOKEN=
LOGGER_ID=
MONGO_DB_URI=
OWNER_ID=
STRING_SESSION=
```

</details>

<details>
<summary><b>Vars and Details :</b></summary>

`API_ID` : Goto [my.telegram.org](https://my.telegram.org) to obtain this.

`API_HASH` : Goto [my.telegram.org](https://my.telegram.org) to obtain this.

`BOT_TOKEN` : Get the bot token from [@BotFather](https://telegram.dog/BotFather)

`OWNER_ID` : Your Telegram User ID

`LOGGER_ID` : Your Telegram Chat ID For logs Where Bot and Assistant Id Should Be Admin!

`STRING_SESSION` : Add String session for assistant to play songs on voice chat.

`DATABASE_URL` : MongoDB URI for saving User IDs when they first Start the Bot.

### Optional Vars

`UPDATES_CHANNEL` : Put a Public Channel Username, so every user have to Join that channel to use the bot. Must add bot to channel as Admin to work properly.

</details>

<details>
<summary><b>How to Use :</b></summary>

⚠️ **Before using the bot, don't forget to add the bot to the `Logger_Chat` as an Admin**

- `/start` : To check if the bot is alive or not.

- `/play` or `/vplay` or `/cplay` : Starts streaming the requested track on videochat.

- `/playforce` or `/vplayforce` or `/cplayforce` : Force play stops the ongoing stream and starts streaming the requested track.

- `/channelplay [chat username or id]` or `[disable]` : Connect channel to a group and starts streaming tracks.

- `/seek` : Seek the stream to the given duration.

- `/seekback` : Backward seek the stream to the given duration.

- `/pause` : Pause the current playing stream.

- `/resume` : Resume the paused stream.

- `/skip` : Skip the current playing stream and start streaming the next track in queue.

- `/end` or `/stop` : Clears the queue and ends the current playing stream.

To get an instant result do `/reboot` in chat of logger.

![image](https://files.catbox.moe/z1h6ow.jpg)

### Channel Support

Bot also Supported with Channels. Just add bot and assistant to the Channel as Admin.

</details>

## ❤️ Credits :

- [Simple Boy](https://github.com/Simple-Boy-1k)
- [Devlepor](https://t.me/Itz_Ego_1k)
- Everyone In This Journey !
