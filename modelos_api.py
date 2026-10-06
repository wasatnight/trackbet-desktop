from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class SeleccionAPI(BaseModel):
    """Representa una selección individual de un parlay."""

    model_config = ConfigDict(extra="ignore")

    deporte: str | None = None
    liga: str | None = None
    evento: str | None = None
    tipo_apuesta: str | None = None
    seleccion: str | None = None
    resultado_seleccion: str | None = None
    cuota_individual: float | int | str | None = None
    cuota_texto_individual: str | None = None
    tipo_cuota_individual: str | None = None


class ApuestaStraightCrearAPI(BaseModel):
    """Datos necesarios para registrar una apuesta straight."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )

    casa: str = Field(
        min_length=1,
        max_length=60,
    )
    deporte: str = Field(
        min_length=1,
        max_length=60,
    )
    liga: str = Field(
        min_length=1,
        max_length=100,
    )
    evento: str = Field(
        min_length=1,
        max_length=200,
    )
    mercado: str = Field(
        min_length=1,
        max_length=100,
    )
    seleccion: str = Field(
        min_length=1,
        max_length=150,
    )

    momento_apuesta: Literal[
        "prepartido",
        "en_vivo",
    ] = "prepartido"

    tipo_cuota: Literal[
        "decimal",
        "americana",
    ]

    cuota: float

    stake: float = Field(
        gt=0,
    )

    modalidad: Literal["straight"] = "straight"
    resultado: Literal["pendiente"] = "pendiente"

    @model_validator(mode="after")
    def validar_cuota(self):
        """Valida la cuota según el formato seleccionado."""

        if self.tipo_cuota == "decimal" and self.cuota <= 1:
            raise ValueError("La cuota decimal debe ser mayor que 1.")

        if self.tipo_cuota == "americana" and -100 < self.cuota < 100:
            raise ValueError(
                "La cuota americana debe ser "
                "igual o menor que -100, "
                "o igual o mayor que +100."
            )

        return self


class SeleccionParlayCrearAPI(BaseModel):
    """Datos de una selección para registrar un parlay."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )

    deporte: str = Field(
        min_length=1,
        max_length=60,
    )
    liga: str = Field(
        min_length=1,
        max_length=100,
    )
    evento: str = Field(
        min_length=1,
        max_length=200,
    )
    mercado: str = Field(
        min_length=1,
        max_length=100,
    )
    seleccion: str = Field(
        min_length=1,
        max_length=150,
    )

    tipo_cuota: Literal[
        "decimal",
        "americana",
    ]

    cuota: float

    resultado_seleccion: Literal["pendiente"] = "pendiente"

    @model_validator(mode="after")
    def validar_cuota_individual(self):
        """Valida la cuota individual de la selección."""

        if self.tipo_cuota == "decimal" and self.cuota <= 1:
            raise ValueError("La cuota decimal individual debe ser mayor que 1.")

        if self.tipo_cuota == "americana" and -100 < self.cuota < 100:
            raise ValueError(
                "La cuota americana individual debe ser "
                "igual o menor que -100, "
                "o igual o mayor que +100."
            )

        return self


class ApuestaParlayCrearAPI(BaseModel):
    """Datos necesarios para registrar una apuesta parlay."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )

    casa: str = Field(
        min_length=1,
        max_length=60,
    )

    momento_apuesta: Literal[
        "prepartido",
        "en_vivo",
    ] = "prepartido"

    selecciones: list[SeleccionParlayCrearAPI] = Field(
        min_length=2,
        max_length=30,
    )

    tipo_cuota: Literal[
        "decimal",
        "americana",
    ]

    cuota: float

    stake: float = Field(
        gt=0,
    )

    modalidad: Literal["parlay"] = "parlay"

    resultado: Literal["pendiente"] = "pendiente"

    @model_validator(mode="after")
    def validar_cuota_final(self):
        """Valida la cuota combinada final del parlay."""

        if self.tipo_cuota == "decimal" and self.cuota <= 1:
            raise ValueError("La cuota decimal final debe ser mayor que 1.")

        if self.tipo_cuota == "americana" and -100 < self.cuota < 100:
            raise ValueError(
                "La cuota americana final debe ser "
                "igual o menor que -100, "
                "o igual o mayor que +100."
            )

        return self


class SeleccionParlayActualizarAPI(BaseModel):
    """Campos editables de una selección existente."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )

    numero: int = Field(ge=1)

    deporte: str | None = Field(
        default=None,
        min_length=1,
        max_length=60,
    )
    liga: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    evento: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    mercado: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    seleccion: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    tipo_cuota: (
        Literal[
            "decimal",
            "americana",
        ]
        | None
    ) = None

    cuota: float | None = None

    @model_validator(mode="after")
    def validar_actualizacion_seleccion(self):
        """Valida los cambios de una selección."""

        campos_enviados = self.model_fields_set - {"numero"}

        if not campos_enviados:
            raise ValueError(
                "Debes enviar al menos un campo para modificar la selección."
            )

        tipo_enviado = "tipo_cuota" in self.model_fields_set
        cuota_enviada = "cuota" in self.model_fields_set

        if tipo_enviado != cuota_enviada:
            raise ValueError(
                "Para cambiar la cuota individual debes "
                "enviar tipo_cuota y cuota juntos."
            )

        if tipo_enviado and cuota_enviada:
            if (
                self.tipo_cuota == "decimal"
                and self.cuota is not None
                and self.cuota <= 1
            ):
                raise ValueError("La cuota decimal individual debe ser mayor que 1.")

            if (
                self.tipo_cuota == "americana"
                and self.cuota is not None
                and -100 < self.cuota < 100
            ):
                raise ValueError(
                    "La cuota americana individual debe ser "
                    "igual o menor que -100, "
                    "o igual o mayor que +100."
                )

        return self


class ApuestaParlayActualizarAPI(BaseModel):
    """Campos editables de una apuesta parlay."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )

    casa: str | None = Field(
        default=None,
        min_length=1,
        max_length=60,
    )

    momento_apuesta: (
        Literal[
            "prepartido",
            "en_vivo",
        ]
        | None
    ) = None

    tipo_cuota: (
        Literal[
            "decimal",
            "americana",
        ]
        | None
    ) = None

    cuota: float | None = None

    stake: float | None = Field(
        default=None,
        gt=0,
    )

    selecciones: list[SeleccionParlayActualizarAPI] | None = Field(
        default=None,
        min_length=1,
    )

    @model_validator(mode="after")
    def validar_actualizacion_parlay(self):
        """Valida la edición parcial del parlay."""

        if not self.model_fields_set:
            raise ValueError("Debes enviar al menos un campo para actualizar.")

        tipo_enviado = "tipo_cuota" in self.model_fields_set
        cuota_enviada = "cuota" in self.model_fields_set

        if tipo_enviado != cuota_enviada:
            raise ValueError(
                "Para cambiar la cuota combinada debes "
                "enviar tipo_cuota y cuota juntos."
            )

        if tipo_enviado and cuota_enviada:
            if (
                self.tipo_cuota == "decimal"
                and self.cuota is not None
                and self.cuota <= 1
            ):
                raise ValueError("La cuota decimal final debe ser mayor que 1.")

            if (
                self.tipo_cuota == "americana"
                and self.cuota is not None
                and -100 < self.cuota < 100
            ):
                raise ValueError(
                    "La cuota americana final debe ser "
                    "igual o menor que -100, "
                    "o igual o mayor que +100."
                )

        selecciones_recibidas: list[SeleccionParlayActualizarAPI] = (
            self.selecciones or []
        )

        numeros = [seleccion.numero for seleccion in selecciones_recibidas]

        if len(numeros) != len(set(numeros)):
            raise ValueError("No puedes repetir el número de una selección.")

        return self


class ResultadoSeleccionParlayAPI(BaseModel):
    """Resultado nuevo para una selección del parlay."""

    model_config = ConfigDict(
        extra="forbid",
    )

    numero: int = Field(
        ge=1,
    )

    resultado: Literal[
        "ganada",
        "perdida",
        "push",
        "pendiente",
    ]


class SeleccionesParlayActualizarAPI(BaseModel):
    """Selecciones del parlay que serán actualizadas."""

    model_config = ConfigDict(
        extra="forbid",
    )

    selecciones: list[ResultadoSeleccionParlayAPI] = Field(
        min_length=1,
    )

    @model_validator(mode="after")
    def validar_numeros_unicos(self):
        """Impide enviar dos veces la misma selección."""

        numeros = [seleccion.numero for seleccion in self.selecciones]

        if len(numeros) != len(set(numeros)):
            raise ValueError("No puedes repetir el número de una selección.")

        return self


class OrdenSeleccionesParlayAPI(BaseModel):
    """Nuevo orden de las selecciones de un parlay."""

    model_config = ConfigDict(
        extra="forbid",
    )

    orden: list[int] = Field(
        min_length=2,
    )

    @model_validator(mode="after")
    def validar_orden(self):
        """Valida números positivos y sin repeticiones."""

        if any(numero < 1 for numero in self.orden):
            raise ValueError(
                "Los números de selección deben ser mayores o iguales que 1."
            )

        if len(self.orden) != len(set(self.orden)):
            raise ValueError("No puedes repetir números en el nuevo orden.")

        return self


class ApuestaStraightActualizarAPI(BaseModel):
    """Campos editables de una apuesta straight."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )

    casa: str | None = Field(
        default=None,
        min_length=1,
        max_length=60,
    )
    deporte: str | None = Field(
        default=None,
        min_length=1,
        max_length=60,
    )
    liga: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    evento: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    mercado: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    seleccion: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    momento_apuesta: (
        Literal[
            "prepartido",
            "en_vivo",
        ]
        | None
    ) = None

    tipo_cuota: (
        Literal[
            "decimal",
            "americana",
        ]
        | None
    ) = None

    cuota: float | None = None

    stake: float | None = Field(
        default=None,
        gt=0,
    )

    @model_validator(mode="after")
    def validar_actualizacion(self):
        """Valida los campos enviados para actualizar."""

        if not self.model_fields_set:
            raise ValueError("Debes enviar al menos un campo para actualizar.")

        tipo_enviado = "tipo_cuota" in self.model_fields_set
        cuota_enviada = "cuota" in self.model_fields_set

        if tipo_enviado != cuota_enviada:
            raise ValueError(
                "Para cambiar la cuota debes enviar tipo_cuota y cuota juntos."
            )

        if tipo_enviado and cuota_enviada:
            if self.tipo_cuota == "decimal" and self.cuota <= 1:
                raise ValueError("La cuota decimal debe ser mayor que 1.")

            if self.tipo_cuota == "americana" and -100 < self.cuota < 100:
                raise ValueError(
                    "La cuota americana debe ser "
                    "igual o menor que -100, "
                    "o igual o mayor que +100."
                )

        return self


class ResultadoApuestaActualizarAPI(BaseModel):
    """Resultado permitido para cerrar una apuesta straight."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    resultado: Literal[
        "ganada",
        "perdida",
        "push",
    ]


class ApuestaAPI(BaseModel):
    """Representa una apuesta devuelta por la API."""

    model_config = ConfigDict(
        extra="ignore",
    )

    id: int
    fecha: str | None = None
    casa: str | None = None
    deporte: str | None = None
    liga: str | None = None
    evento: str | None = None
    mercado: str | None = None
    seleccion: str | None = None
    momento_apuesta: str | None = None
    modalidad: str | None = None

    tipo_cuota: str | None = None
    cuota_texto: str | None = None
    cuota: float | int | str | None = None

    stake: float | int | str | None = None
    resultado: str | None = None

    cuota_liquidada: float | int | str | None = None

    tipo_cuota_liquidada: str | None = None
    cuota_liquidada_texto: str | None = None

    retorno_total_real: float | int | str | None = None

    selecciones: list[SeleccionAPI] = Field(default_factory=list)


class SeleccionEliminadaParlayAPI(BaseModel):
    """Respuesta después de eliminar una selección de un parlay."""

    mensaje: str
    numero_eliminado: int
    seleccion_eliminada: SeleccionAPI
    apuesta: ApuestaAPI


class ApuestaEliminadaAPI(BaseModel):
    """Respuesta devuelta después de eliminar una apuesta."""

    mensaje: str
    id_eliminado: int
    apuesta: ApuestaAPI


class EstadoAPI(BaseModel):
    """Respuesta del estado general de la API."""

    aplicacion: str
    version: str
    estado: str


class ListaApuestasAPI(BaseModel):
    """Respuesta paginada del listado de apuestas."""

    total: int
    cantidad: int
    limite: int
    desplazamiento: int
    orden: str
    filtros: dict[str, str]
    apuestas: list[ApuestaAPI]


class ListaPendientesAPI(BaseModel):
    """Respuesta del listado de apuestas pendientes."""

    total: int
    apuestas: list[ApuestaAPI]


class RendimientoMomentoAPI(BaseModel):
    """Rendimiento de apuestas por momento."""

    apuestas: int
    stake: float
    ganadas: int
    perdidas: int
    push: int
    ganancia: float
    win_rate: float
    roi: float


class StakesRecomendadosAPI(BaseModel):
    """Stakes recomendados según bankroll."""

    stake_1: float
    stake_2: float
    stake_3: float


class ResumenApuestaEstadisticaAPI(BaseModel):
    """Información resumida de una apuesta."""

    id: int | None = None
    evento: str
    mercado: str
    seleccion: str
    ganancia: float


class ResumenCategoriaEstadisticaAPI(BaseModel):
    """Mejor o peor categoría de rendimiento."""

    nombre: str
    ganancia: float


class AnalisisRangoCuotaAPI(BaseModel):
    """Rendimiento de un rango de cuotas."""

    rango: str
    resueltas: int
    decididas: int
    ganadas: int
    perdidas: int
    push: int
    stake: float
    ganancia: float
    cuota_promedio: float
    win_rate: float
    probabilidad_implicita: float
    diferencia_equilibrio: float
    roi: float
    muestra: str
    alertas: list[str]


class AnalisisCuotasAPI(BaseModel):
    """Análisis completo por rangos de cuotas."""

    total_apuestas: int
    apuestas_validas: int
    rangos: list[AnalisisRangoCuotaAPI]
    nota: str


class RendimientoParlayCategoriaAPI(BaseModel):
    """Rendimiento de una categoría de parlays."""

    registrados: int
    resueltos: int
    pendientes: int
    ganadas: int
    perdidas: int
    push: int
    stake: float
    ganancia: float
    decididas: int
    win_rate: float
    roi: float
    muestra: str


class ResultadosSeleccionesParlayAPI(BaseModel):
    """Conteo de resultados individuales."""

    ganadas: int
    perdidas: int
    push: int
    pendientes: int
    sin_resultado: int


class ComparacionCuotasParlayAPI(BaseModel):
    """Comparación de cuota calculada y ofrecida."""

    id: int | str | None = None
    selecciones: int
    tipo_eventos: str
    cuota_producto: float
    cuota_ofrecida: float
    diferencia: float


class AnalisisParlaysAPI(BaseModel):
    """Análisis completo de las apuestas parlay."""

    total_apuestas: int
    parlays_registrados: int
    parlays_resueltos: int
    parlays_pendientes: int

    rendimiento_piernas: dict[
        str,
        RendimientoParlayCategoriaAPI,
    ]

    rendimiento_deportes: dict[
        str,
        RendimientoParlayCategoriaAPI,
    ]

    rendimiento_eventos: dict[
        str,
        RendimientoParlayCategoriaAPI,
    ]

    resultados_selecciones: ResultadosSeleccionesParlayAPI

    mercados_perdidos: dict[str, int]
    deportes_perdidos: dict[str, int]

    comparaciones_cuotas: list[ComparacionCuotasParlayAPI]

    nota: str


class DiagnosticoAPI(BaseModel):
    """Diagnóstico seguro expuesto mediante la API."""

    nombre_app: str
    version_app: str
    estado_general: str

    almacenamiento: str

    tamano_base_datos: int | float
    tamano_base_datos_formateado: str

    tablas_validas: bool
    tablas_faltantes: list[str]
    base_datos_sqlite: bool

    apuestas_registradas: int
    selecciones_registradas: int

    bankroll_inicial: float
    ganancia_neta: float
    bankroll_actual: float

    apuestas_pendientes: int
    stake_pendiente: float

    ultimo_respaldo_disponible: bool
    ultimo_respaldo_fecha: str | None = None

    problemas_integridad: list[str]
    cantidad_problemas_integridad: int


class ResumenInteligenteEstadisticasAPI(BaseModel):
    """Principales fortalezas y debilidades."""

    mejor_deporte: ResumenCategoriaEstadisticaAPI | None = None

    peor_deporte: ResumenCategoriaEstadisticaAPI | None = None

    mejor_mercado: ResumenCategoriaEstadisticaAPI | None = None

    peor_mercado: ResumenCategoriaEstadisticaAPI | None = None


class EstadisticasAPI(BaseModel):
    """Estadísticas completas de TrackBet."""

    total_apostado: float
    ganadas: int
    perdidas: int
    push: int
    pendientes: int
    stake_pendiente: float
    ganancia_neta: float
    apuestas_decididas: int
    win_rate: float
    roi: float

    bankroll_inicial: float
    bankroll_actual: float
    cambio_bankroll: float

    stakes_recomendados: StakesRecomendadosAPI

    rendimiento_deportes: dict[
        str,
        float,
    ]
    rendimiento_casas: dict[
        str,
        float,
    ]
    rendimiento_modalidades: dict[
        str,
        float,
    ]
    rendimiento_mercados: dict[
        str,
        float,
    ]
    rendimiento_ligas: dict[
        str,
        float,
    ]

    rendimiento_momentos: dict[
        str,
        RendimientoMomentoAPI,
    ]

    mejor_apuesta: ResumenApuestaEstadisticaAPI | None = None

    peor_apuesta: ResumenApuestaEstadisticaAPI | None = None

    resumen_inteligente: ResumenInteligenteEstadisticasAPI

    alertas: list[str]


class ResumenFinancieroAPI(BaseModel):
    """Respuesta del resumen financiero."""

    model_config = ConfigDict(extra="ignore")

    bankroll_inicial: float
    ganancia_neta: float
    bankroll_actual: float
    stake_total: float
    stake_resuelto: float
    stake_pendiente: float
    roi: float
    apuestas_totales: int
    apuestas_resueltas: int
    apuestas_pendientes: int


class BankrollAPI(BaseModel):
    """Configuración actual del bankroll."""

    bankroll_inicial: float


class BankrollActualizarAPI(BaseModel):
    """Datos permitidos para actualizar el bankroll."""

    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
    )

    bankroll_inicial: float = Field(
        ge=0,
    )
