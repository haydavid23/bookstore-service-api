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
    def from_dict(cls, data: Dict[str, Any]) -> "CreateProfileDTO":
        required_fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]

        if "role" in data:
            raise ValueError("role cannot be set during profile creation")

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
            role="user",
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
            id=user.id,
            username=user.username,
            email=user.email,
            address=user.address,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
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

        if "role" in data:
            raise ValueError("role cannot be updated")

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

@dataclass
class CreateCreditCardDTO:
    card_number: str
    expiration_date: date | None = None
    cvv: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CreateCreditCardDTO":
        card_number = data.get("card_number")

        if not isinstance(card_number, str) or not card_number.strip():
            raise ValueError("card_number is required")

        expiration_date = data.get("expiration_date")

        if expiration_date is not None:
            if not isinstance(expiration_date, str) or not expiration_date.strip():
                raise ValueError("expiration_date must be a date string")

            try:
                expiration_date = date.fromisoformat(expiration_date)
            except ValueError:
                raise ValueError("expiration_date must use YYYY-MM-DD format")
         
        cvv = data.get("cvv")

        if cvv is not None and (
            not isinstance(cvv, int) or isinstance(cvv, bool)
        ):
            raise ValueError("cvv must be an integer")

        return cls(
            card_number=card_number.strip(),
            expiration_date=expiration_date,
            cvv=cvv,
        )

@dataclass
class CreditCardResponseDTO:
    id: int
    card_number: str
    user_profile_id: int
    expiration_date: date | None = None

    @classmethod
    def from_model(cls, credit_card) -> "CreditCardResponseDTO":
        return cls(
            id=credit_card.id,
            card_number=credit_card.card_number,
            user_profile_id=credit_card.user_profile_id,
            expiration_date=credit_card.expiration_date,
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)

        if self.expiration_date is not None:
            data["expiration_date"] = self.expiration_date.isoformat()

        return data
