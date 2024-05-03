from dataclasses import dataclass, field


@dataclass
class EdgeData:
    relative_angle: float = field(init=False, default=0, repr=True, compare=True, hash=True)
    length: float = field(init=False, default=0, repr=True, compare=True, hash=True)
    thickness: float = field(init=False, default=0, repr=True, compare=True, hash=True)
    generation: int = field(init=False, default=0, repr=True, compare=True, hash=True)
    end_to_end_length: float = field(init=False, default=0, repr=True, compare=True, hash=True)
