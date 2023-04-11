const Discord = require('discord.js');
const { Client, Intents } = require('discord.js');
const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES, Intents.FLAGS.GUILD_MESSAGE_REACTIONS] });
const token = require('./config/token');
const terms = require('./terms');
const re = require('re');
const Karma = require('./karma');

const intents = new Discord.Intents(Discord.Intents.ALL);
intents.remove('GUILD_PRESENCES');
intents.remove('GUILD_MEMBERS');

const bot = new Discord.Client({ intents });
const karma = new Karma();
const valid_attachments = [".wav", ".mp3", ".flac"];

// This code is creating a list called `required_words` by iterating over a list called `terms` and
// appending each term in lowercase to the `required_words` list. This is likely being done to later
// check if a message contains any of the required words in order to earn a "feedback karma point".

const required_words = [];
for (const term of terms) {
    required_words.push(term.toLowerCase());
}

// Some filtering configuration values for the module

const min_characters = 280;
const required_url_pattern = /^(https?:\/\/)?(www\.)?(soundcloud|youtube|clyp\.it|drive|onedrive|dropbox|bandcamp|mixcloud)\./;


// Commands for retreiving Karma point balance for themselves or another user
// Plan to place this in an embed. 

bot.on('messageCreate', async (message) => {
    if (message.author.bot) {
        return;
    }

    console.log(`Channel name: ${message.channel.name}`);
    console.log(`Channel type: ${message.channel.type}`);

    if (message.channel.type === 'GUILD_PUBLIC_THREAD') {
        console.log('Processing message in forum channel');

        const thread_id = message.channel.id;
        const user_id = message.author.id;

        if (!karma.get_threads().includes(thread_id)) {
            karma.add_thread(thread_id);
        }

        if (!karma.user_in_thread(thread_id, user_id)) {
            const parent_messages = await message.channel.messages.fetch({ limit: 1 });
            const parent_message = parent_messages.first();

            // This code block is checking if the initial post in a public thread contains a valid URL or a valid
            // audio file attachment. If it does not meet these requirements, the initial post is deleted and a
            // message is sent to the author of the post notifying them that their post did not meet the
            // requirements.

            if (!re.test(required_url_pattern, parent_message.content)) {
                console.log('Initial post does not contain a valid URL');
                const has_valid_attachment = parent_message.attachments.some(att => valid_attachments.includes(att.name.toLowerCase()));
                if (!has_valid_attachment) {
                    console.log('Initial post does not contain a valid audio file attachment');
                    await parent_message.delete();
                    await message.channel.send(`${parent_message.author.toString()}, your post did not meet the requirements (URL or audio file attachment).`);
                    return;
                }
            }

            // This code block is checking if the author of the current message is the same as the author of the
            // initial post in a public thread. If the authors are the same, it means that the current message was
            // posted by the same user who created the thread, and therefore no "feedback karma" should be awarded.
            // The code prints a message saying that "no reward" will be given and returns without awarding any
            // "feedback karma".

            if (message.author.id === parent_message.author.id) {
                console.log('Message author is the initial poster - no reward');
                return;
            }

            // This code block is checking if the length of the message content is greater than or equal to the
            // value of `min_characters`. If it is, the message meets the length requirement and the code continues
            // to check for other criteria to award "feedback karma". If it is not, the message does not meet the
            // length requirement and the code returns without awarding any "feedback karma".

            if (message.content.length >= min_characters) {
                console.log('Message length requirement met');
            } else {
                console.log('Message length requirement not met');
                return;
            }

            // This code block is checking if a message contains any of the required words in the `required_words`
            // list. If it does, the code prints a message saying that "karma will be awarded". If it does not, the
            // code prints a message saying that "karma will not be awarded" and returns without awarding any
            // "feedback karma".

            if (required_words.some(word => message.content.toLowerCase().includes(word))) {
                console.log('Message contains required words - karma will be awarded');
            } else {
                console.log('Message does not contain required words - karma will not be awarded');
                return;
            }

            // This code block is awarding "feedback karma" to a user who has posted a message in a public thread
            // that meets certain criteria.

            karma.add_user_to_thread(thread_id, user_id);
            if (karma.user_exists(user_id)) {
                karma.increment_user_karma(user_id);
            } else {
                karma.add_user(user_id);
            }

            karma.save();
            await message.react('✅');
            await message.channel.send(`${message.author.toString()} has earned 1 feedback Karma!`);
        }
    }
});

// Commands for retreiving Karma point balance for themselves or another user
// Plan to place this in an embed.

bot.on('messageCreate', async (message) => {
    if (message.content.startsWith('!getkarma')) {
        const user = message.mentions.users.first();

        if (!user) {
            await message.reply('Please mention a user to check their karma points.');
            return;
        }

        const user_id = user.id;
        const user_karma = karma.get_users()[user_id] || 0;
        console.log(`Karma balance was retrieved via bot command for ${user.toString()}`);
        await message.reply(`${user.toString()} has ${user_karma} feedback karma points!`);
    } else if (message.content.startsWith('!mykarma')) {
        const user_id = message.author.id;
        const user_karma = karma.get_users()[user_id] || 0;
        console.log(`${message.author.toString()} retrieved their own Karma balance`);
        await message.reply(`${message.author.toString()}, you have ${user_karma} feedback karma points!`);
    }
});

// Commands for setting allowed file types which are required to initiate a feedback request
// Manage messages permission is required to use the commands.

bot.on('messageCreate', async (message) => {
    if (!message.member.permissions.has('MANAGE_MESSAGES')) {
        return;
    }

    if (message.content.startsWith('!add_extension')) {
        const [, filetype] = message.content.split(' ');

        if (!filetype) {
            await message.reply('Please add a file extension to add to the whitelist.');
            return;
        }

        if (!valid_attachments.includes(filetype)) {.
            valid_attachments.push(filetype);
            console.log(`${message.author.toString()} has added ${filetype} to the whitelist`);
            await message.reply(`${filetype} has been added to the list of allowed extensions.`);
        } else {
            await message.reply(`${filetype} is already in the whitelist.`);
        }
    } else if (message.content.startsWith('!remove_extension')) {
        const [, filetype] = message.content.split(' ');

        if (!filetype) {
            await message.reply('Please add a file extension to remove it from the whitelist.');
            return;
        }

        if (valid_attachments.includes(filetype)) {
            valid_attachments.splice(valid_attachments.indexOf(filetype), 1);
            console.log(`${message.author.toString()} has removed ${filetype} from the whitelist`);
            await message.reply(`${filetype} has been removed from the list of allowed extensions.`);
        } else {
            await message.reply(`${filetype} is not on the whitelist.`);
        }
    }
});

// Ready the bot

bot.on('ready', () => {
    console.log(`${bot.user.tag} is now enforcing feedback!`);
});

bot.login(token);