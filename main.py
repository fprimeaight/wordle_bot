import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from database import Database
from game import Wordle
from image import board_image, score_graph

load_dotenv('.env')
TOKEN: str = os.getenv('TOKEN')
PYMONGO_CONNECTION = os.getenv('PYMONGO_CONNECTION')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
pymongo_db = Database(PYMONGO_CONNECTION)

@bot.event
async def on_ready():
    print('Bot is running!')
    try:
        await bot.tree.sync()
    except Exception as e:
        print(f'Error: {e}')

    activity = discord.Game(name='Play Wordle with this bot!')
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.tree.command(name='new_game', description='Start a new game of Wordle!')
async def new_game(interaction:discord.Interaction):
    game = Wordle()
    game.generate_solution()
    data = pymongo_db.find_user(interaction.user.id)

    if not data:
        pymongo_db.insert_user(interaction.user.id, game)
    else:
        if pymongo_db.get_user_game(interaction.user.id): 
            pymongo_db.update_user_total_games(interaction.user.id, 
                                               pymongo_db.get_user_total_games(interaction.user.id) + 1)
        
        pymongo_db.update_user_game(interaction.user.id, game)
    

    desc = f'''This is your Game No. {pymongo_db.get_user_total_games(interaction.user.id) + 1} \nUse /guess to enter a word!\nUse /help to learn how to play!'''

    embed = discord.Embed(title='WORDLE!',
                          description=desc,
                          colour=0x1bb899)

    file = board_image(game.board, game.keyboard)
    embed.set_image(url="attachment://image.png")

    await interaction.response.send_message(embed=embed, file=file)

@bot.tree.command(name='guess', description='Make a Wordle guess!')
async def guess(interaction:discord.Interaction, word:str):
    data = pymongo_db.find_user(interaction.user.id)

    if (not data or not data['game_serial']):
        embed = discord.Embed(title='You have not started a game yet!',
                              description=f'Use /new_game to start a Wordle game!',
                              colour=0xe05361)
        await interaction.response.send_message(embed=embed)
    else:
        game = pymongo_db.get_user_game(interaction.user.id)
        if not game.check_word_exists(word):
            embed = discord.Embed(title='Word is not valid!',
                                    description=f'Ensure that your word has 5 letters and is an existing word!',
                                    colour=0xe05361)
            await interaction.response.send_message(embed=embed)
        else:
            game.eval_word(word)

            if game.check_win(word):
                embed = discord.Embed(title='YOU WON!',
                                        description=f'You got the word in {game.curr_row} attempts!',
                                        colour=0x7bba43)
                file = board_image(game.board, game.keyboard)
                embed.set_image(url="attachment://image.png")
                total_games = pymongo_db.get_user_total_games(interaction.user.id)
                score = pymongo_db.get_user_score(interaction.user.id)
                score[game.curr_row - 1] += 1
                pymongo_db.update_user_score(interaction.user.id, score)
                pymongo_db.update_user_total_games(interaction.user.id, total_games + 1)
                game = None
                pymongo_db.update_user_game(interaction.user.id, game)
                await interaction.response.send_message(embed=embed, file=file)
            elif game.check_lose():
                embed = discord.Embed(title='YOU LOSE!',
                                        description=f'The word was {game.solution}!',
                                        colour=0xe05361)
                file = board_image(game.board, game.keyboard)
                embed.set_image(url="attachment://image.png")
                total_games = pymongo_db.get_user_total_games(interaction.user.id)
                pymongo_db.update_user_total_games(interaction.user.id, total_games + 1)
                game = None
                pymongo_db.update_user_game(interaction.user.id, game)
                await interaction.response.send_message(embed=embed, file=file)
            else:
                desc = f'''Use /guess to enter a word! \nUse /help to learn how to play!'''
                embed = discord.Embed(title='WORDLE!',
                                        description=desc,
                                        colour=0x1bb899)
                pymongo_db.update_user_game(interaction.user.id, game)
                file = board_image(game.board, game.keyboard)
                embed.set_image(url="attachment://image.png")
                await interaction.response.send_message(embed=embed, file=file)

@bot.tree.command(name='profile', description='Shows user statistics!')
async def profile(interaction:discord.Interaction):
    data = pymongo_db.find_user(interaction.user.id)
    if not data:
        desc = f'''Play a game to access your statistics.\nUse /new_game to start a Wordle game!'''
        embed = discord.Embed(title='No statistics yet!',
                              description=desc,
                              colour=0xe05361)
        await interaction.response.send_message(embed=embed)
    else:
        total_games = data['total_games']
        score = data['score']
        total_wins = sum(score)
        
        avg_guesses = 0
        for i in range(len(score)):
            avg_guesses += score[i] * (i + 1)
        avg_guesses /= total_wins
        stats_desc = f'''🔹 Total Games: {total_games}\n🔹 Total Wins: {total_wins}\n🔹 Win Percentage: {(total_wins / total_games * 100):.2f}%\n🔹 Avg. Guesses Per Win: {avg_guesses:.2f}'''
    
        embed = discord.Embed(title='Profile',
                              description=f'User statistics for {interaction.user.name}...',
                              colour=0x1bb899)
        
        embed.add_field(name='Statistics',
                        value=stats_desc,
                        inline=False)
        
        embed.add_field(name='Guess Distribution',
                        value='')
        
        file = score_graph(score)
        embed.set_image(url="attachment://image.png")
        embed.set_thumbnail(url=interaction.user.avatar)
        await interaction.response.send_message(embed=embed, file=file)

@bot.tree.command(name='leaderboard', description='Shows server leaderboard!')
async def leaderboard(interaction:discord.Interaction):
    if not interaction.guild:
        embed = discord.Embed(title='Cannot access server leaderboard!',
                              description=f'This command only works in servers, not DMs!',
                              colour=0xe05361)
        await interaction.response.send_message(embed=embed)
    else:
        leaderboard = pymongo_db.get_leaderboard()
        leaderboard_copy = [None for i in range(5)]

        index = 0
        for data in leaderboard:
            if interaction.guild.get_member(data['_id']):
                leaderboard_copy[index] = data
                index += 1

                if index >= 5:
                    break
        
        embed = discord.Embed(title='Server Leaderboard',
                              description=f'Showing users with the most wins...',
                              colour=0x1bb899)
        
        for index, data in enumerate(leaderboard_copy):
            if data:
                avg_guesses = 0
                if sum(data['score']) > 0:
                    for i in range(len(data['score'])):
                        avg_guesses += data['score'][i] * (i + 1)
                    avg_guesses /= sum(data['score'])
                leaderboard_desc = f'''Total Wins: {sum(data['score'])}\nTotal Games: {data['total_games']}\nAverage Guesses: {avg_guesses:.2f}'''

                embed.add_field(name=f'#{index + 1} - {interaction.guild.get_member(data['_id'])}',
                                value=leaderboard_desc,
                                inline=False)
            else: 
                leaderboard_desc = f'''Total Wins: 0\nTotal Games: 0\nAverage Guesses: 0.00'''

                embed.add_field(name=f'#{index + 1} - None',
                                value=leaderboard_desc,
                                inline=False)
        
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name='help', description='Guide on how to use this bot!')
async def help(interaction:discord.Interaction):
    embed = discord.Embed(title='Help',
                          description=f'',
                          colour=0x1bb899)
    
    help_desc = f'''You have 6 tries to guess a 5 letter word.\nThe colour of the tiles will change according to how close your guess was to the word.\nGreen tiles mean that the letter is in the word and in the correct spot.\nYellow tiles mean that the letter is in the word but is in the incorrect spot.\nGrey tiles mean that the letter is not found in the word.'''
    
    command_desc = f'''🔹 **/new_game** - Start a new game of Wordle!\n🔹 **/guess** - Guess a 5 letter word in your current Wordle game!\n🔹 **/profile** - View all your relevant user statistics!\n🔹 **/leaderboard** - View server leaderboards! (Only works in servers)\n🔹 **/help** - View instructions on how to use this bot!'''
    
    embed.add_field(name='How to play',
                    value=help_desc,
                    inline=False)
    
    embed.add_field(name='Commands',
                    value=command_desc,
                    inline=False)
    
    await interaction.response.send_message(embed=embed)
    
if __name__ == '__main__':
    bot.run(TOKEN)
