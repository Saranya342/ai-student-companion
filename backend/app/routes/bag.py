from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database.connection import SessionLocal
from app.database import models
from app.routes.auth import get_current_user

router = APIRouter()

class BagItemCreate(BaseModel):
    day: str
    item_name: str

class BagItemUpdate(BaseModel):
    is_checked: str

DEFAULT_ITEMS = {
    "Monday":    ["ID card", "Notebook", "Pen", "Water bottle"],
    "Tuesday":   ["ID card", "Lab coat", "Record book", "Pen"],
    "Wednesday": ["ID card", "Notebook", "Calculator", "Pen"],
    "Thursday":  ["ID card", "Lab coat", "Record book", "Pen"],
    "Friday":    ["ID card", "Notebook", "Pen", "Water bottle"],
    "Saturday":  ["ID card", "Notebook", "Pen"],
    "Sunday":    []
}


@router.get("/day/{day}")
def get_bag_for_day(day: str, current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        day = day.capitalize()
        items = db.query(models.BagItem).filter(
            models.BagItem.user_id == current_user.id,
            models.BagItem.day == day
        ).all()

        if not items and day in DEFAULT_ITEMS:
            for item_name in DEFAULT_ITEMS[day]:
                db.add(models.BagItem(
                    day=day,
                    item_name=item_name,
                    is_checked="false",
                    user_id=current_user.id
                ))
            db.commit()
            items = db.query(models.BagItem).filter(
                models.BagItem.user_id == current_user.id,
                models.BagItem.day == day
            ).all()

        return {
            "day": day,
            "total": len(items),
            "checked": sum(1 for i in items if i.is_checked == "true"),
            "items": [
                {
                    "id": item.id,
                    "item_name": item.item_name,
                    "is_checked": item.is_checked
                }
                for item in items
            ]
        }
    finally:
        db.close()


@router.post("/item/add")
def add_bag_item(req: BagItemCreate, current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        day = req.day.capitalize()
        existing = db.query(models.BagItem).filter(
            models.BagItem.user_id == current_user.id,
            models.BagItem.day == day,
            models.BagItem.item_name == req.item_name
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Item already exists for this day")

        new_item = models.BagItem(
            day=day,
            item_name=req.item_name,
            is_checked="false",
            user_id=current_user.id
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        return {
            "message": "Item added ✅",
            "item": {
                "id": new_item.id,
                "day": new_item.day,
                "item_name": new_item.item_name,
                "is_checked": new_item.is_checked
            }
        }
    finally:
        db.close()


@router.put("/item/check/{item_id}")
def check_item(item_id: int, req: BagItemUpdate, current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        item = db.query(models.BagItem).filter(
            models.BagItem.id == item_id,
            models.BagItem.user_id == current_user.id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        item.is_checked = req.is_checked
        db.commit()

        return {
            "message": "Updated ✅",
            "item_id": item_id,
            "is_checked": req.is_checked
        }
    finally:
        db.close()


@router.delete("/item/delete/{item_id}")
def delete_item(item_id: int, current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        item = db.query(models.BagItem).filter(
            models.BagItem.id == item_id,
            models.BagItem.user_id == current_user.id
        ).first()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        db.delete(item)
        db.commit()

        return {"message": f"'{item.item_name}' deleted ✅"}
    finally:
        db.close()


@router.put("/day/reset/{day}")
def reset_day(day: str, current_user: models.User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        day = day.capitalize()
        items = db.query(models.BagItem).filter(
            models.BagItem.user_id == current_user.id,
            models.BagItem.day == day
        ).all()

        for item in items:
            item.is_checked = "false"
        db.commit()

        return {"message": f"All items for {day} unchecked ✅"}
    finally:
        db.close()