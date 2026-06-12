from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class CreateProfileDTO:
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    address: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CreateProfileDTO":
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
    address: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "ProfileResponseDTO":
        return cls(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            address=row.get("address"),
            first_name=row["first_name"],
            last_name=row["last_name"],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)