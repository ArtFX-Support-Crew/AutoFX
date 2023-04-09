const Discord = require('discord.js');
const fs = require('fs');
const client = new Discord.Client({ intents: ["GUILDS", "GUILD_MESSAGES", "GUILD_MEMBERS", "GUILD_MESSAGE_REACTIONS", "GUILD_MESSAGE_CONTENT"] });

const requiredWords = ['drums', 'snare', 'low', 'high', 'mix', 'compression', 'womp', 'burrrrrrrrr', 'transient', 'reese'];
const minCharacters = 280;

function loadKarmaData() {
    return JSON.parse(fs.readFileSync('karma.json', 'utf8'));
}

function saveKarmaData(data) {
    fs.writeFileSync('karma.json', JSON.stringify(data, null, 4));
}

client.on('ready', () => {
    console.log(`${client.user.username} is now enforcing feedback!`);
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) {
        return;
    }

    console.log(`Channel name: ${message.channel.name}`);
    console.log(`Channel type: ${message.channel.type}`);

    if (message.channel.type === 'GUILD_PUBLIC_THREAD') {
        console.log("Processing message in forum channel");

        const threadId = message.channel.id;
        const userId = message.author.id;
        const data = loadKarmaData();

        if (!(threadId in data.threads)) {
            console.log("Thread not in data. Creating new thread entry.");
            data.threads[threadId] = [];
        }

        if (!data.threads[threadId].includes(userId)) {
            console.log("User has not earned karma in this thread");

            // Get the initial message in the thread
            const parentMessage = (await message.channel.messages.fetch({ limit: 1 })).first();

            if (message.author.id === parentMessage.author.id) {
                console.log("Message author is the initial poster");
                return;
            }

            if (message.content.length >= minCharacters) {
                console.log("Message length requirement met");
            } else {
                console.log("Message length requirement not met");
                return;
            }

            if (requiredWords.some(word => message.content.toLowerCase().includes(word))) {
                console.log("Message contains required words");
            } else {
                console.log("Message does not contain required words");
                return;
            }

            data.threads[threadId].push(userId);

            if (userId in data.users) {
                data.users[userId] += 1;
            } else {
                data.users[userId] = 1;
            }

            saveKarmaData(data);
            await message.react('✅');
            await message.channel.send(`${message.author.toString()} has earned 1 feedback karma point!`);
        }
    }
});

client.login ('MTA0MzU2NzM1ODExNzE2NzE4NA.G4Y7iX.YPPfzTtWAmbKQUGn6UxBazjJvm6Gnae47nZ2nQ')