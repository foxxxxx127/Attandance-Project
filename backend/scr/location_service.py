from geopy.distance import geodesic
import setting

class LocationService:
    @staticmethod
    def validate_coordinates(current, reference) -> dict:
        """
        验证GPS坐标有效性
        返回: {
            "valid": bool,
            "distance": float,
            "accuracy": float
        }
        """
        try:
            distance = geodesic(current, reference).km
            return {
                "valid": distance <= setting.GPS_TOLERANCE_KM,
                "distance": round(distance, 3),
                "accuracy": current.get("accuracy", 0)
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}