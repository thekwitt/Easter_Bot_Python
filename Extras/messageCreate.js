const { MessageActionRow, MessageButton, MessageEmbed } = require('discord.js');

function clarify(id1, id2)
{
	if(id1 == id2) return 'SUCCESS';
	return 'DANGER';
}

async function fuck(message, client, channel_id) {
	const messageSpawn = client.messages.get(message.guild.id);
	if (messageSpawn.get('timestamp') < Math.floor(Date.now() / 1000) && messageSpawn.get('messageCount') <= 1 && messageSpawn.get('activeMessage') == false) {
		// eslint-disable-next-line prefer-const
		let ids = [];
		messageSpawn.set('activeMessage', true);
		client.messages.set(message.guild.id, messageSpawn);

		const data = await client.pool.query('SELECT * FROM guild_settings WHERE Guild_ID = $1', [message.guild.id]);
		const setting = data.rows[0];

		let embed = undefined;
		const percent = Math.floor(Math.random() * 100);
		let rarity = 1;
		let present = client.extra.getRandom(client.presents.filter(p => p.type == 'Regular' && p.gifted == false));
		let num = (Number(String(present.id).slice(-2)) - 1) % 7;
		const intros = ['*A present falls from the sky!*', '*The present taunts you with anticipation.*', '*Suddenly out of the blue, there is a present in front of you.*', '*George, the potted plant of the North Pole, greets you with a present.*'];
		embed = new MessageEmbed()
			.setColor(client.colors[0][1])
			.setTitle('🌟   A ' + present.name + ' suddenly appeared!   🌟')
			// eslint-disable-next-line spaced-comment
			//.setThumbnail(user.defaultAvatarURL)
			.setDescription('⠀\n' + client.extra.getRandom(intros) + '\n\n' + '**Press the button that looks like the present in the picture below to get it!**\n⠀')
			.setFooter('You only have one chance to collect this present!')
			.setImage(present.url);

		let tempArr = [num];
		while (tempArr.length < 3) {
			const r = client.extra.random(0, 6);
			if(tempArr.indexOf(r) === -1) tempArr.push(r);
		}
		tempArr = client.extra.shuffle(tempArr);
		let row = new MessageActionRow()
			.addComponents(
				new MessageButton()
					.setCustomId(String(tempArr[0]))
					.setEmoji(String(client.icons[tempArr[0]]))
					.setStyle('SUCCESS')
					.setDisabled(false),
			)
			.addComponents(
				new MessageButton()
					.setCustomId(String(tempArr[1]))
					.setEmoji(String(client.icons[tempArr[1]]))
					.setStyle('SUCCESS')
					.setDisabled(false),
			)
			.addComponents(
				new MessageButton()
					.setCustomId(String(tempArr[2]))
					.setEmoji(String(client.icons[tempArr[2]]))
					.setStyle('SUCCESS')
					.setDisabled(false),
			);

		let finishedRow = new MessageActionRow()
			.addComponents(
				new MessageButton()
					.setCustomId(String(tempArr[0]))
					.setEmoji(String(client.icons[tempArr[0]]))
					.setStyle(clarify(tempArr[0], num))
					.setDisabled(true),
			)
			.addComponents(
				new MessageButton()
					.setCustomId(String(tempArr[1]))
					.setEmoji(String(client.icons[tempArr[1]]))
					.setStyle(clarify(tempArr[1], num))
					.setDisabled(true),
			)
			.addComponents(
				new MessageButton()
					.setCustomId(String(tempArr[2]))
					.setEmoji(String(client.icons[tempArr[2]]))
					.setStyle(clarify(tempArr[2], num))
					.setDisabled(true),
			);

		if(percent < 5) { // Glitched
			present = client.extra.getRandom(client.presents.filter(p => p.type == 'Glitched' && p.gifted == false));
			num = 7;
			rarity = 3;
			embed = new MessageEmbed()
				.setColor(client.colors[0][1])
				.setTitle('🌟   A ' + present.name + ' suddenly appeared!   🌟')
				// eslint-disable-next-line spaced-comment
				//.setThumbnail(user.defaultAvatarURL)
				.setDescription('⠀\n' + client.extra.getRandom(intros) + '\n\n' + '**Press the button that looks like the present in the picture below to get it!**\n⠀')
				.setFooter('You only have one chance to collect this present!')
				.setImage(present.url);

			tempArr = [num];
			while (tempArr.length < 5) {
				const r = client.extra.random(0, 6);
				if(tempArr.indexOf(r) === -1) tempArr.push(r);
			}
			tempArr = client.extra.shuffle(tempArr);
			row = new MessageActionRow()
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[0]))
						.setEmoji(String(client.icons[tempArr[0]]))
						.setStyle('SUCCESS')
						.setDisabled(false),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[1]))
						.setEmoji(String(client.icons[tempArr[1]]))
						.setStyle('SUCCESS')
						.setDisabled(false),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[2]))
						.setEmoji(String(client.icons[tempArr[2]]))
						.setStyle('SUCCESS')
						.setDisabled(false),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[3]))
						.setEmoji(String(client.icons[tempArr[3]]))
						.setStyle('SUCCESS')
						.setDisabled(false),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[4]))
						.setEmoji(String(client.icons[tempArr[4]]))
						.setStyle('SUCCESS')
						.setDisabled(false),
				);

			finishedRow = new MessageActionRow()
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[0]))
						.setEmoji(String(client.icons[tempArr[0]]))
						.setStyle(clarify(tempArr[0], num))
						.setDisabled(true),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[1]))
						.setEmoji(String(client.icons[tempArr[1]]))
						.setStyle(clarify(tempArr[1], num))
						.setDisabled(true),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[2]))
						.setEmoji(String(client.icons[tempArr[2]]))
						.setStyle(clarify(tempArr[2], num))
						.setDisabled(true),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[3]))
						.setEmoji(String(client.icons[tempArr[3]]))
						.setStyle(clarify(tempArr[3], num))
						.setDisabled(true),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[4]))
						.setEmoji(String(client.icons[tempArr[4]]))
						.setStyle(clarify(tempArr[4], num))
						.setDisabled(true),
				);
		}

		else if(percent < 35) { // Lucky
			present = client.extra.getRandom(client.presents.filter(p => p.type == 'Lucky' && p.gifted == false));
			rarity = 2;
			num = (Number(String(present.id).slice(-2)) - 1) % 7;
			embed = new MessageEmbed()
				.setColor(client.colors[0][1])
				.setTitle('🌟   A ' + present.name.replace('Square ', '').replace('Circle  ', '').replace('Rectangle  ', '') + ' suddenly appeared!   🌟')
				// eslint-disable-next-line spaced-comment
				//.setThumbnail(user.defaultAvatarURL)
				.setDescription('⠀\n' + client.extra.getRandom(intros) + '\n\n' + '**Press the button that looks like the present in the picture below to get it!**\n⠀')
				.setFooter('You only have one chance to collect this present!')
				.setImage(present.url);

			tempArr = [num];
			while (tempArr.length < 4) {
				const r = client.extra.random(0, 5);
				if(tempArr.indexOf(r) === -1) tempArr.push(r);
			}
			tempArr = client.extra.shuffle(tempArr);
			row = new MessageActionRow()
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[0]))
						.setEmoji(String(client.icons[tempArr[0]]))
						.setStyle('SUCCESS')
						.setDisabled(false),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[1]))
						.setEmoji(String(client.icons[tempArr[1]]))
						.setStyle('SUCCESS')
						.setDisabled(false),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[2]))
						.setEmoji(String(client.icons[tempArr[2]]))
						.setStyle('SUCCESS')
						.setDisabled(false),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[3]))
						.setEmoji(String(client.icons[tempArr[3]]))
						.setStyle('SUCCESS')
						.setDisabled(false),
				);

			finishedRow = new MessageActionRow()
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[0]))
						.setEmoji(String(client.icons[tempArr[0]]))
						.setStyle(clarify(tempArr[0], num))
						.setDisabled(true),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[1]))
						.setEmoji(String(client.icons[tempArr[1]]))
						.setStyle(clarify(tempArr[1], num))
						.setDisabled(true),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[2]))
						.setEmoji(String(client.icons[tempArr[2]]))
						.setStyle(clarify(tempArr[2], num))
						.setDisabled(true),
				)
				.addComponents(
					new MessageButton()
						.setCustomId(String(tempArr[3]))
						.setEmoji(String(client.icons[tempArr[3]]))
						.setStyle(clarify(tempArr[3], num))
						.setDisabled(true),
				);
		}

		let channel = undefined;
		channel = await message.guild.channels.cache.get(channel_id.toString());
		let interactionMessage = undefined;
		try{interactionMessage = await channel.send({ embeds: [embed], components: [row] }).then(client.extra.log_g(client.logger, message.guild, 'Message Create Event', 'First Send'));}
		catch { 
			client.extra.log_error_g(client.logger, message.guild, 'Message Create Event', 'Send Denied');
			messageSpawn.set('messageCount', setting.message_count).set('timestamp', Math.floor(Date.now() / 1000) + setting.message_interval).set('activeMessage', false);
			client.messages.set(message.guild.id, messageSpawn);
		}
		await client.pool.query('UPDATE guild_stats SET messages_spawned = messages_spawned + 1 WHERE Guild_ID = $1', [message.guild.id]);
		if(interactionMessage == undefined) return ;

		const filter = i => {
			return i.message.id == interactionMessage.id;
		};

		const collector = await channel.createMessageComponentCollector({ filter, time: 60000, maxUsers: setting.obtain_amount });
		collector.on('collect', async i => {
			await client.pool.query('INSERT INTO guild_data (Guild_ID, Member_ID) VALUES ($1, $2) ON CONFLICT DO NOTHING;', [message.guild.id, message.author.id]);
			if (ids.includes(i.user.id)) {
				try{await i.reply({ content: 'You already tried to get a present!', ephemeral: true }).then(client.extra.log_g(client.logger, message.guild, 'Message Create Event', 'Already Present Reply'));}
				catch{client.extra.log_error_g(client.logger, message.guild, 'Message Create Event', 'Reply Denied');}
			}
			else if (collector.users.size > setting.obtain_amount) {
				try{await i.reply({ content: 'Oh no! You were too late! Someone grabbed the last present.', ephemeral: true }).then(client.extra.log_g(client.logger, message.guild, 'Message Create Event', 'Too Late Present Reply'));}
				catch{client.extra.log_error_g(client.logger, message.guild, 'Message Create Event', 'Reply Denied');}
			}
			else if (i.customId === String(num)) {
				ids.push(i.user.id);
				await client.pool.query('UPDATE guild_data SET presents = array_append(presents,$1), collected = collected + 1 WHERE Guild_ID = $3 AND Member_ID = $2;', [present.id, i.user.id, message.guild.id]);
				// eslint-disable-next-line max-statements-per-line
				await client.pool.query('UPDATE guild_stats SET Presents_Collected = Presents_Collected + 1 WHERE Guild_ID = $1', [message.guild.id]);
				const strings = ['*You firmly grasp the present and put it in your holiday sack.*', '*You jump around happily and squeal louder than your life depends on it as you put the present in your holiday sack.*', '*Your holiday sack engulfs the present on its own. You stare at the holiday sack as it returns to an inanimate object.*', '*You poke the present with curiosity and slowly tug at the ribbon. Startled, the present jumps into the holiday sack shaking furiously.*', '*You have an anime battle with the present. Fortunately your power exceeds the very soul the present possesses.*', '*You examine the present and conclude that it is worth unwrapping later.*', '*Mahogany.*', '*The present has a casual conversation with you as it trips and falls into your holiday sack.*', '*Santa laughs as he puts the present in your holiday sack.*'];
				const wow = ['', ' Woah! You got a present!', 'Awesome! You got a lucky present!', 'Unbelieveable! You got a glitched present'];
				embed = new MessageEmbed()
					.setColor(client.colors[0][1])
					.setTitle(wow[rarity])
					// eslint-disable-next-line spaced-comment
					//.setThumbnail(user.defaultAvatarURL)
					.setDescription('⠀\n' + client.extra.getRandom(strings) + '\n\nNice! You now have a new present! Go ahead and check it out with **/sack** !\n⠀')
					.setFooter('Make sure to pay attention on the next bunch!');
				try{await i.reply({ embeds: [embed], ephemeral: true }).then(client.extra.log_g(client.logger, message.guild, 'Message Create Event', i.user.username + ' - Present Reply'));}
				catch{client.extra.log_error_g(client.logger, message.guild, 'Message Create Event', 'Reply Denied');}

			}
			else {
				ids.push(i.user.id);
				const strings = ['*In the end, it was no present. In fact it was just a lump of coal.*', '*You crush the present with your feet and it morphs into coal that is stuck on the bottom of your shoe.*', '*The present vanishes. Maybe the real present was the friend\'s we made along the way. But sadly all you got was coal.*', '*You were impatient and opened the present too early. What you find inside makes you suffer regret.*', '*The present realizes you are not a good person and spits coal at you.*', '*Turns out it was someone else\'s present. As you take it into your hands, you open it up to only find the finest coal ever made.*', '*Santa frowns upon you. In disappointment, he hands you some coal.*'];
				embed = new MessageEmbed()
					.setColor(client.colors[0][1])
					.setTitle('Oh no! You picked the wrong present!')
					// eslint-disable-next-line spaced-comment
					//.setThumbnail(user.defaultAvatarURL)
					.setDescription('⠀\n' + client.extra.getRandom(strings) + '\n\n**You now have a lump of coal in your toybox!**\n⠀')
					.setFooter('Make sure to pay attention on the next bunch!');
				await client.pool.query('UPDATE guild_stats SET Coal_Collected = Coal_Collected + 1 WHERE Guild_ID = $1', [message.guild.id]);
				await client.pool.query('UPDATE guild_data SET toys = array_append(toys,$1) WHERE Guild_ID = $3 AND Member_ID = $2;', [[7001, 7002, 7003][rarity - 1], i.user.id, message.guild.id]);
				// eslint-disable-next-line max-statements-per-line
				try{await i.reply({ embeds: [embed], ephemeral: true }).then(client.extra.log_g(client.logger, message.guild, 'Message Create Event', 'Present Failed Reply'));}
				catch{client.extra.log_error_g(client.logger, message.guild, 'Message Create Event', 'Reply Denied');}
			}

		});
		// eslint-disable-next-line no-unused-vars
		collector.on('end', async i => {
			if(collector.users.size < setting.obtain_amount) {
				const strings = ['*The present flew away, never to be seen again.*', '*Connection to the present was lost.*', '*The present didn\'t feel wanted and started becoming depressed. The sad little box hopped away.*'];
				embed = new MessageEmbed()
					.setColor(client.colors[0][1])
					.setTitle('The present vanished!')
					// eslint-disable-next-line spaced-comment
					//.setThumbnail(user.defaultAvatarURL)
					.setDescription('⠀\n' + client.extra.getRandom(strings) + '\n\n**Keep on talking for another one to appear!**\n⠀')
					.setFooter('Each bunch only lasts 60 seconds!');
				try{await interactionMessage.edit({ embeds: [embed], components: [finishedRow] }).then(client.extra.log_g(client.logger, message.guild, 'Message Create Event', 'Expired Edit'));}
				catch{client.extra.log_error_g(client.logger, message.guild, 'Message Create Event', 'Edit Denied');}
			}
			else {
				embed = new MessageEmbed()
					.setColor(client.colors[0][1])
					.setTitle('Everyone took from the bunch!')
					// eslint-disable-next-line spaced-comment
					//.setThumbnail(user.defaultAvatarURL)
					.setDescription('⠀\nKeep on talking for another one to appear!\n⠀')
					.setFooter('Each bunch only lasts 60 seconds!');
				try{await interactionMessage.edit({ embeds: [embed], components: [finishedRow] }).then(client.extra.log_g(client.logger, message.guild, 'Message Create Event', 'Empty Edit'));}
				catch{client.extra.log_error_g(client.logger, message.guild, 'Message Create Event', 'Edit Denied');}
			}
			messageSpawn.set('messageCount', setting.message_count).set('timestamp', Math.floor(Date.now() / 1000) + setting.message_interval).set('activeMessage', false);
			client.messages.set(message.guild.id, messageSpawn);
		});
	}
	else {
		messageSpawn.set('messageCount', messageSpawn.get('messageCount') - 1);
		client.messages.set(message.guild.id, messageSpawn);
	}
}

module.exports = {
	name: 'messageCreate',
	async execute(message, client) {
		if(!message.deleted && message.member != null)
		{
			await client.pool.query('INSERT INTO guild_data (Guild_ID, Member_ID) VALUES ($1, $2) ON CONFLICT DO NOTHING;', [message.guild.id, message.author.id]);
			const data = await client.pool.query('SELECT * FROM guild_settings WHERE Guild_ID = $1', [message.guild.id]);
			const setting = data.rows[0];

			// Check Channel ID
			const list = message.guild.channels.cache.filter(c => c.type === 'GUILD_TEXT');
			if(!list.has(setting.channel_set) && setting.channel_set != 0) {

				await client.pool.query('UPDATE guild_settings SET channel_set = 0 WHERE Guild_ID = $1', [message.guild.id]);
			}

			if(setting.channel_set != 0) {
				if(setting.trigger_outside) {
					if(client.ready.every(v => v === true) && message.member.user.bot == false) {
						await fuck(message, client, setting.channel_set);
					}
				} else if (message.channel.id == setting.channel_set) {
					if(client.ready.every(v => v === true) && message.member.user.bot == false) {
						await fuck(message, client, setting.channel_set);
					}
				}
			}
		}
	},
};