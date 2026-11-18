"""
Módulo models.py
Define as classes de domínio, herança, polimorfismo e exceções personalizadas
do Sistema de Reservas de Hotel.
Autor: Rodrigo Henry Dortha Manancas (Matrícula: 202503754306)
"""

from datetime import datetime


class ReservaException(Exception):
    """Exceção base personalizada para erros de regra de negócio do hotel."""
    pass


class QuartoIndisponivelError(ReservaException):
    """Lançada quando o quarto já possui reserva conflitante no período solicitado."""
    pass


class DataInvalidaError(ReservaException):
    """Lançada quando a data de check-out é anterior ou igual à data de check-in."""
    pass


class Cliente:
    """Representa um cliente (hóspede) cadastrado no hotel."""

    def __init__(self, nome: str, documento: str, telefone: str, email: str = ""):
        self.nome = nome.strip()
        self.documento = documento.strip()
        self.telefone = telefone.strip()
        self.email = email.strip()

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "documento": self.documento,
            "telefone": self.telefone,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Cliente":
        return cls(
            nome=dados["nome"],
            documento=dados["documento"],
            telefone=dados["telefone"],
            email=dados.get("email", ""),
        )

    def __str__(self) -> str:
        return f"{self.nome} (CPF/Doc: {self.documento} | Tel: {self.telefone})"


class Quarto:
    """Classe base que representa uma acomodação genérica do hotel."""

    def __init__(self, numero: int, capacidade: int, diaria_base: float):
        self.numero = int(numero)
        self.capacidade = int(capacidade)
        self.diaria_base = float(diaria_base)

    def tipo_acomodacao(self) -> str:
        return "Padrão"

    def calcular_valor_total(self, dias: int) -> float:
        """Cálculo base de diárias (sobrescrito nas subclasses — Polimorfismo)."""
        return self.diaria_base * dias

    def to_dict(self) -> dict:
        return {
            "numero": self.numero,
            "tipo": self.tipo_acomodacao(),
            "capacidade": self.capacidade,
            "diaria_base": self.diaria_base,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Quarto":
        tipo = dados.get("tipo", "Solteiro")
        numero = dados["numero"]
        diaria = dados["diaria_base"]
        if tipo == "Solteiro":
            return QuartoSolteiro(numero, diaria)
        elif tipo == "Casal":
            return QuartoCasal(numero, diaria)
        elif tipo == "Suíte":
            return QuartoSuite(numero, diaria)
        return cls(numero, dados.get("capacidade", 1), diaria)

    def __str__(self) -> str:
        return (
            f"Quarto {self.numero} [{self.tipo_acomodacao()}] - "
            f"Cap.: {self.capacidade} pessoa(s) - R$ {self.diaria_base:.2f}/noite"
        )


class QuartoSolteiro(Quarto):
    """Subclasse de Quarto para acomodação individual (Herança)."""

    def __init__(self, numero: int, diaria_base: float = 150.0):
        super().__init__(numero=numero, capacidade=1, diaria_base=diaria_base)

    def tipo_acomodacao(self) -> str:
        return "Solteiro"

    def calcular_valor_total(self, dias: int) -> float:
        # Desconto de 5% para estadias a partir de 5 diárias
        subtotal = self.diaria_base * dias
        return subtotal * 0.95 if dias >= 5 else subtotal


class QuartoCasal(Quarto):
    """Subclasse de Quarto para acomodação de casal (Herança)."""

    def __init__(self, numero: int, diaria_base: float = 240.0):
        super().__init__(numero=numero, capacidade=2, diaria_base=diaria_base)

    def tipo_acomodacao(self) -> str:
        return "Casal"

    def calcular_valor_total(self, dias: int) -> float:
        # Inclui taxa fixa de café da manhã especial de R$ 25,00 por diária
        return (self.diaria_base + 25.0) * dias


class QuartoSuite(Quarto):
    """Subclasse de Quarto para Suíte Executiva/Luxo (Herança)."""

    def __init__(self, numero: int, diaria_base: float = 420.0):
        super().__init__(numero=numero, capacidade=4, diaria_base=diaria_base)

    def tipo_acomodacao(self) -> str:
        return "Suíte"

    def calcular_valor_total(self, dias: int) -> float:
        # Inclui taxa de serviço VIP de 10% sobre o valor das diárias
        return (self.diaria_base * dias) * 1.10


class Reserva:
    """Associa um Cliente a um Quarto em um intervalo de datas de check-in e check-out."""

    FORMATO_DATA = "%d/%m/%Y"

    def __init__(
        self,
        id_reserva: int,
        cliente: Cliente,
        quarto: Quarto,
        data_checkin: str,
        data_checkout: str,
        status: str = "Ativa",
    ):
        self.id_reserva = int(id_reserva)
        self.cliente = cliente
        self.quarto = quarto
        self.dt_checkin = self.validar_formato_data(data_checkin)
        self.dt_checkout = self.validar_formato_data(data_checkout)

        if self.dt_checkout <= self.dt_checkin:
            raise DataInvalidaError(
                "A data de check-out deve ser posterior à data de check-in."
            )

        self.status = status
        self.dias = (self.dt_checkout - self.dt_checkin).days
        self.valor_total = self.quarto.calcular_valor_total(self.dias)

    @classmethod
    def validar_formato_data(cls, data_str: str) -> datetime:
        try:
            return datetime.strptime(data_str.strip(), cls.FORMATO_DATA)
        except ValueError as exc:
            raise DataInvalidaError(
                f"Data '{data_str}' inválida. Utilize o formato DD/MM/AAAA."
            ) from exc

    def conflita_com(self, checkin_novo: datetime, checkout_novo: datetime) -> bool:
        """Verifica se há sobreposição de datas para uma reserva ativa."""
        if self.status != "Ativa":
            return False
        return (checkin_novo < self.dt_checkout) and (checkout_novo > self.dt_checkin)

    def to_dict(self) -> dict:
        return {
            "id_reserva": self.id_reserva,
            "cliente": self.cliente.to_dict(),
            "quarto": self.quarto.to_dict(),
            "data_checkin": self.dt_checkin.strftime(self.FORMATO_DATA),
            "data_checkout": self.dt_checkout.strftime(self.FORMATO_DATA),
            "dias": self.dias,
            "valor_total": round(self.valor_total, 2),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Reserva":
        cliente = Cliente.from_dict(dados["cliente"])
        quarto = Quarto.from_dict(dados["quarto"])
        return cls(
            id_reserva=dados["id_reserva"],
            cliente=cliente,
            quarto=quarto,
            data_checkin=dados["data_checkin"],
            data_checkout=dados["data_checkout"],
            status=dados.get("status", "Ativa"),
        )

    def __str__(self) -> str:
        checkin_str = self.dt_checkin.strftime(self.FORMATO_DATA)
        checkout_str = self.dt_checkout.strftime(self.FORMATO_DATA)
        return (
            f"Reserva #{self.id_reserva:03d} [{self.status}] | "
            f"Quarto {self.quarto.numero} ({self.quarto.tipo_acomodacao()}) | "
            f"Hóspede: {self.cliente.nome} | "
            f"Período: {checkin_str} a {checkout_str} ({self.dias} diária(s)) | "
            f"Total: R$ {self.valor_total:.2f}"
        )
