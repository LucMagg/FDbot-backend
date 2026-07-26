from flask import current_app
from app.models.grid import Grid


class GridService:

  @staticmethod
  def create_grid(grid_data):
    grid = Grid.from_dict(grid_data)
    return grid.create(current_app.mongo_db)
  
  @staticmethod
  def get_all_grids():
    return Grid.read_all(current_app.mongo_db)
  
  @staticmethod
  def update_grid(grid_data):
    return Grid.update_one(current_app.mongo_db, grid_data)