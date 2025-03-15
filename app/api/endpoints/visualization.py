from fastapi import APIRouter, Depends, HTTPException, Form
from app.api.endpoints import auth
from app.schema.schemas import PlotData, VizualizeSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.services.data_processing.data_preprocess import get_columns, get_example_file , get_plot_url
from app.services.visualization.plot_pipeline import plot_pipeline
from app.db.models import Vizualize

router = APIRouter(dependencies=[Depends(auth.get_current_user)])


@router.post("/chose-plot")
async def chose_plot(data: PlotData,
                    user: dict = Depends(auth.get_current_user), 
                    db: AsyncSession = Depends(get_async_session)):

    if data.example:
        data.fileUrl = get_example_file(data.viz_type)
    try:
        new_vizualize = Vizualize(
            user_id=user.id,  
            viz_type=data.viz_type,
            viz_data=data.fileUrl,
            )
        
        db.add(new_vizualize)
        await db.flush() 
        await db.commit() 
        await db.refresh(new_vizualize)  
        
        columns = get_columns(data.fileUrl)

        return {"viz_id": new_vizualize.id, "columns": columns,"viz_type": data.viz_type}
    
    except:
        raise HTTPException(status_code=400, detail="Invalid data")

@router.post("/vizualize")
async def vizualize(data:VizualizeSchema,
                    user: dict = Depends(auth.get_current_user), 
                    db: AsyncSession = Depends(get_async_session)):
    
    file_url, plot_type = await get_plot_url(Vizualize, data.plot_id)

    plot = plot_pipeline(file_url, plot_type, data.meta_data, data.viz_id)

    return plot




