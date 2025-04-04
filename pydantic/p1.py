import nest_asyncio
nest_asyncio.apply()

from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
import os

os.system('clear')

model = GroqModel('llama-3.3-70b-versatile')
agent = Agent(model)

Question="When was the first computer bug found?"
result = agent.run_sync(Question)  
print(f"{Question}:\n{'='*len(Question)}\n{result.data}")