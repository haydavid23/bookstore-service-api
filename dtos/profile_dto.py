from dataclasses import asdict, dataclass
from typing import Any, Optional, Dict


@dataclass
class CreateProfileDTO:
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    address: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateProfileDTO":
        required_fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]

        for field in required_fields:
            value = data.get(field)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} is required")

        address = data.get("address")

        if address is not None and not isinstance(address, str):
            raise ValueError("address must be a string")

        return cls(
            username=data["username"].strip(),
            email=data["email"].strip(),
            first_name=data["first_name"].strip(),
            last_name=data["last_name"].strip(),
            password=data["password"],
            address=address.strip() if address else None,
        )


@dataclass
class ProfileResponseDTO:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    address: Optional[str] = None

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "ProfileResponseDTO":
        return cls(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            address=row.get("address"),
            first_name=row["first_name"],
            last_name=row["last_name"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UpdateProfileDTO:
    updates: Dict[str, Optional[str]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpdateProfileDTO":
        allowed_fields = {
            "username",
            "first_name",
            "last_name",
            "address",
            "password",
        }

        if "email" in data:
            raise ValueError("email cannot be updated")

        unexpected_fields = set(data) - allowed_fields

        if unexpected_fields:
            unexpected = ", ".join(sorted(unexpected_fields))
            raise ValueError(f"Unexpected field(s): {unexpected}")

        if not data:
            raise ValueError("At least one user field is required")

        updates: Dict[str, Optional[str]] = {}

        for field, value in data.items():
            if field == "address":
                if value is not None and not isinstance(value, str):
                    raise ValueError("address must be a string or null")

                updates[field] = value.strip() if value else None
                continue

            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")

            updates[field] = value.strip()

        return cls(updates=updates)
