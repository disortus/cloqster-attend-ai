from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from postgres import database
from sqlites import reg_user

router = Router()

@router.message(CommandStart())
async def start_bot(message: types.Message):
    
