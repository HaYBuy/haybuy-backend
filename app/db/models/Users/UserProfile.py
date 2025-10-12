from sqlalchemy import Column, String, Boolean, Float, TIMESTAMP, Integer, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
import datetime
from app.db.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    phone = Column(String , nullable=True)
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    district = Column(String, nullable=True)
    province = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_verified = Column(Boolean, default=False)
    id_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User", back_populates="profile")

    @property
    def location_dict(self):
        if self.latitude is not None and self.longitude is not None:
            return {"lat": self.latitude, "lng": self.longitude}
        return None
