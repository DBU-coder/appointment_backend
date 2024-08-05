from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Patient, User

from .abstract import Repository


class PatientRepository(Repository[Patient]):

    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Patient, session=session)

    async def new(self, data) -> Patient:
        user = User(**data.model_dump())
        patient = Patient(user=user)
        self.session.add(patient)
        await self.session.commit()
        return patient
