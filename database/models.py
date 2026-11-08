
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    func
)

from database.connection import Base


# =====================================================
# 1. PRODUCT TABLE
# =====================================================

class Product(Base):

    __tablename__ = "products"

    product_id = Column(String(20), primary_key=True)
    product_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    unit_of_measure = Column(String(20), nullable=False)

    lifecycle_status = Column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    __table_args__ = (
        CheckConstraint(
            "lifecycle_status IN ('ACTIVE', 'INACTIVE')",
            name="ck_product_status"
        ),
    )


# =====================================================
# 2. SUPPLIER TABLE
# =====================================================

class Supplier(Base):

    __tablename__ = "suppliers"

    supplier_id = Column(String(20), primary_key=True)
    supplier_name = Column(String(100), nullable=False)
    supplier_location = Column(String(100), nullable=False)
    supplier_category = Column(String(50), nullable=False)
    quality_rating = Column(Float, nullable=False)

    lifecycle_status = Column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    __table_args__ = (
        CheckConstraint(
            "quality_rating >= 0 AND quality_rating <= 100",
            name="ck_supplier_quality_rating"
        ),
        CheckConstraint(
            "lifecycle_status IN ('ACTIVE', 'INACTIVE')",
            name="ck_supplier_status"
        ),
    )


# =====================================================
# 3. MACHINE TABLE
# =====================================================

class Machine(Base):

    __tablename__ = "machines"

    machine_id = Column(String(20), primary_key=True)
    machine_name = Column(String(100), nullable=False)
    machine_type = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    installation_date = Column(Date, nullable=False)

    lifecycle_status = Column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    __table_args__ = (
        CheckConstraint(
            "lifecycle_status IN ('ACTIVE', 'MAINTENANCE', 'INACTIVE')",
            name="ck_machine_status"
        ),
    )


# =====================================================
# 4. BOM TABLE
# =====================================================

class BOM(Base):

    __tablename__ = "boms"

    bom_id = Column(String(30), primary_key=True)

    product_id = Column(
        String(20),
        ForeignKey("products.product_id"),
        nullable=False
    )

    version = Column(Integer, nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)

    lifecycle_status = Column(
        String(20),
        nullable=False,
        default="DRAFT"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "version",
            name="uq_product_bom_version"
        ),
        CheckConstraint(
            "version > 0",
            name="ck_bom_version"
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_bom_dates"
        ),
        CheckConstraint(
            "lifecycle_status IN ('DRAFT', 'ACTIVE', 'OBSOLETE')",
            name="ck_bom_status"
        ),
    )


# =====================================================
# 5. BOM MATERIAL LINES TABLE
# =====================================================

class BOMLine(Base):

    __tablename__ = "bom_lines"

    bom_line_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    bom_id = Column(
        String(30),
        ForeignKey("boms.bom_id"),
        nullable=False
    )

    material_code = Column(String(30), nullable=False)
    material_description = Column(String(100), nullable=False)
    quantity_required = Column(Float, nullable=False)
    unit_of_measure = Column(String(20), nullable=False)

    scrap_allowance_pct = Column(
        Float,
        nullable=False,
        default=0
    )

    __table_args__ = (
        UniqueConstraint(
            "bom_id",
            "material_code",
            name="uq_bom_material"
        ),
        CheckConstraint(
            "quantity_required > 0",
            name="ck_bom_quantity"
        ),
        CheckConstraint(
            "scrap_allowance_pct >= 0 AND scrap_allowance_pct <= 100",
            name="ck_bom_scrap"
        ),
    )


# =====================================================
# 6. MATERIAL LOT TABLE
# =====================================================

class MaterialLot(Base):

    __tablename__ = "material_lots"

    lot_id = Column(String(50), primary_key=True)

    supplier_id = Column(
        String(20),
        ForeignKey("suppliers.supplier_id"),
        nullable=False
    )

    material_code = Column(String(30), nullable=False)
    supplier_batch_number = Column(String(50), nullable=False)

    received_quantity = Column(Float, nullable=False)
    available_quantity = Column(Float, nullable=False)

    unit_of_measure = Column(String(20), nullable=False)

    received_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)

    inspection_status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    lifecycle_status = Column(
        String(20),
        nullable=False,
        default="AVAILABLE"
    )

    __table_args__ = (
        UniqueConstraint(
            "supplier_id",
            "supplier_batch_number",
            name="uq_supplier_batch"
        ),
        CheckConstraint(
            "received_quantity > 0",
            name="ck_lot_received_quantity"
        ),
        CheckConstraint(
            "available_quantity >= 0 AND available_quantity <= received_quantity",
            name="ck_lot_available_quantity"
        ),
        CheckConstraint(
            "expiry_date IS NULL OR expiry_date >= received_date",
            name="ck_lot_expiry"
        ),
        CheckConstraint(
            "inspection_status IN ('PENDING', 'ACCEPTED', 'REJECTED')",
            name="ck_lot_inspection"
        ),
        CheckConstraint(
            "lifecycle_status IN ('AVAILABLE', 'PARTIALLY_USED', 'CONSUMED', 'QUARANTINED')",
            name="ck_lot_status"
        ),
    )


# =====================================================
# 7. PRODUCTION ORDER TABLE
# =====================================================

class ProductionOrder(Base):

    __tablename__ = "production_orders"

    order_id = Column(String(30), primary_key=True)

    product_id = Column(
        String(20),
        ForeignKey("products.product_id"),
        nullable=False
    )

    bom_id = Column(
        String(30),
        ForeignKey("boms.bom_id"),
        nullable=False
    )

    planned_quantity = Column(Integer, nullable=False)
    actual_quantity = Column(Integer, nullable=False, default=0)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    priority = Column(
        String(20),
        nullable=False,
        default="MEDIUM"
    )

    lifecycle_status = Column(
        String(20),
        nullable=False,
        default="PLANNED"
    )

    __table_args__ = (
        CheckConstraint(
            "planned_quantity > 0",
            name="ck_order_planned_quantity"
        ),
        CheckConstraint(
            "actual_quantity >= 0",
            name="ck_order_actual_quantity"
        ),
        CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH')",
            name="ck_order_priority"
        ),
        CheckConstraint(
            "lifecycle_status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')",
            name="ck_order_status"
        ),
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_order_dates"
        ),
    )


# =====================================================
# 8. MATERIAL CONSUMPTION TABLE
# =====================================================

class MaterialConsumption(Base):

    __tablename__ = "material_consumptions"

    consumption_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_id = Column(
        String(30),
        ForeignKey("production_orders.order_id"),
        nullable=False
    )

    lot_id = Column(
        String(50),
        ForeignKey("material_lots.lot_id"),
        nullable=False
    )

    material_code = Column(String(30), nullable=False)

    consumed_quantity = Column(Float, nullable=False)

    consumption_date = Column(DateTime, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "consumed_quantity > 0",
            name="ck_consumed_quantity"
        ),
    )


# =====================================================
# 9. PROCESS STEP TABLE
# =====================================================

class ProcessStep(Base):

    __tablename__ = "process_steps"

    step_id = Column(String(30), primary_key=True)

    order_id = Column(
        String(30),
        ForeignKey("production_orders.order_id"),
        nullable=False
    )

    machine_id = Column(
        String(20),
        ForeignKey("machines.machine_id"),
        nullable=False
    )

    step_name = Column(String(100), nullable=False)
    sequence_number = Column(Integer, nullable=False)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)

    temperature = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)

    process_status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "sequence_number",
            name="uq_order_step_sequence"
        ),
        CheckConstraint(
            "sequence_number > 0",
            name="ck_step_sequence"
        ),
        CheckConstraint(
            "end_time IS NULL OR end_time >= start_time",
            name="ck_step_dates"
        ),
        CheckConstraint(
            "process_status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')",
            name="ck_process_status"
        ),
    )


# =====================================================
# 10. ORDER MACHINE EXECUTION TABLE
# =====================================================

class OrderMachineExecution(Base):

    __tablename__ = "order_machine_executions"

    execution_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_id = Column(
        String(30),
        ForeignKey("production_orders.order_id"),
        nullable=False
    )

    machine_id = Column(
        String(20),
        ForeignKey("machines.machine_id"),
        nullable=False
    )

    step_id = Column(
        String(30),
        ForeignKey("process_steps.step_id"),
        nullable=False
    )

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "end_time IS NULL OR end_time >= start_time",
            name="ck_execution_dates"
        ),
    )

# =====================================================
# 11. INSPECTION PLAN TABLE
# =====================================================

class InspectionPlan(Base):

    __tablename__ = "inspection_plans"

    inspection_plan_id = Column(String(30), primary_key=True)

    product_id = Column(
        String(20),
        ForeignKey("products.product_id"),
        nullable=False
    )

    inspection_name = Column(String(100), nullable=False)
    characteristic = Column(String(100), nullable=False)

    inspection_stage = Column(
        String(30),
        nullable=False
    )

    lower_limit = Column(Float, nullable=True)
    upper_limit = Column(Float, nullable=True)

    unit_of_measure = Column(String(20), nullable=True)

    sample_size = Column(Integer, nullable=False)

    lifecycle_status = Column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    __table_args__ = (
        CheckConstraint(
            "sample_size > 0",
            name="ck_inspection_sample_size"
        ),
        CheckConstraint(
            "lower_limit IS NULL OR upper_limit IS NULL OR upper_limit >= lower_limit",
            name="ck_inspection_limits"
        ),
        CheckConstraint(
            "inspection_stage IN ('INCOMING', 'IN_PROCESS', 'FINAL')",
            name="ck_inspection_stage"
        ),
        CheckConstraint(
            "lifecycle_status IN ('ACTIVE', 'INACTIVE')",
            name="ck_inspection_plan_status"
        ),
    )


# =====================================================
# 12. INSPECTION RESULT TABLE
# =====================================================

class InspectionResult(Base):

    __tablename__ = "inspection_results"

    inspection_id = Column(String(40), primary_key=True)

    inspection_plan_id = Column(
        String(30),
        ForeignKey("inspection_plans.inspection_plan_id"),
        nullable=False
    )

    order_id = Column(
        String(30),
        ForeignKey("production_orders.order_id"),
        nullable=False
    )

    execution_id = Column(
        Integer,
        ForeignKey("order_machine_executions.execution_id"),
        nullable=True
    )

    inspection_date = Column(DateTime, nullable=False)

    inspected_quantity = Column(Integer, nullable=False)
    passed_quantity = Column(Integer, nullable=False, default=0)
    failed_quantity = Column(Integer, nullable=False, default=0)

    measured_value = Column(Float, nullable=True)

    inspection_status = Column(
        String(20),
        nullable=False
    )

    inspector_name = Column(String(100), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "inspected_quantity > 0",
            name="ck_inspected_quantity"
        ),
        CheckConstraint(
            "passed_quantity >= 0 AND failed_quantity >= 0",
            name="ck_inspection_result_quantities"
        ),
        CheckConstraint(
            "passed_quantity + failed_quantity <= inspected_quantity",
            name="ck_inspection_quantity_reconciliation"
        ),
        CheckConstraint(
            "inspection_status IN ('PASS', 'FAIL', 'CONDITIONAL')",
            name="ck_inspection_result_status"
        ),
    )


# =====================================================
# 13. DEFECT TABLE
# =====================================================

class Defect(Base):

    __tablename__ = "defects"

    defect_id = Column(String(30), primary_key=True)

    inspection_id = Column(
        String(40),
        ForeignKey("inspection_results.inspection_id"),
        nullable=False
    )

    order_id = Column(
        String(30),
        ForeignKey("production_orders.order_id"),
        nullable=False
    )

    execution_id = Column(
        Integer,
        ForeignKey("order_machine_executions.execution_id"),
        nullable=True
    )

    lot_id = Column(
        String(50),
        ForeignKey("material_lots.lot_id"),
        nullable=True
    )

    defect_category = Column(String(50), nullable=False)
    defect_description = Column(String(500), nullable=False)

    defect_quantity = Column(Integer, nullable=False)

    severity = Column(
        String(20),
        nullable=False
    )

    detected_at = Column(DateTime, nullable=False)

    defect_status = Column(
        String(20),
        nullable=False,
        default="OPEN"
    )

    __table_args__ = (
        CheckConstraint(
            "defect_quantity > 0",
            name="ck_defect_quantity"
        ),
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="ck_defect_severity"
        ),
        CheckConstraint(
            "defect_status IN ('OPEN', 'UNDER_REVIEW', 'CONTAINED', 'RESOLVED')",
            name="ck_defect_status"
        ),
    )

# =====================================================
# 14. CORRECTIVE ACTION (CAPA) TABLE
# =====================================================

class CorrectiveAction(Base):

    __tablename__ = "corrective_actions"

    capa_id = Column(String(30), primary_key=True)

    defect_id = Column(
        String(30),
        ForeignKey("defects.defect_id"),
        nullable=False
    )

    root_cause = Column(String(1000), nullable=True)

    containment_action = Column(String(1000), nullable=True)

    corrective_action = Column(String(1000), nullable=True)

    preventive_action = Column(String(1000), nullable=True)

    assigned_to = Column(String(100), nullable=False)

    opened_at = Column(DateTime, nullable=False)

    due_date = Column(Date, nullable=False)

    verified_at = Column(DateTime, nullable=True)

    closed_at = Column(DateTime, nullable=True)

    verification_result = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    lifecycle_status = Column(
        String(30),
        nullable=False,
        default="OPEN"
    )

    __table_args__ = (

        CheckConstraint(
            "verification_result IN ('PENDING', 'PASSED', 'FAILED')",
            name="ck_capa_verification"
        ),

        CheckConstraint(
            "lifecycle_status IN ('OPEN', 'INVESTIGATION', 'ACTION_IN_PROGRESS', 'VERIFICATION', 'CLOSED', 'CANCELLED')",
            name="ck_capa_status"
        ),

        CheckConstraint(
            "closed_at IS NULL OR verified_at IS NOT NULL",
            name="ck_capa_verified_before_closure"
        ),

        CheckConstraint(
            "closed_at IS NULL OR verification_result = 'PASSED'",
            name="ck_capa_successful_verification"
        ),

        CheckConstraint(
            "verified_at IS NULL OR verified_at >= opened_at",
            name="ck_capa_verification_date"
        ),

        CheckConstraint(
            "closed_at IS NULL OR closed_at >= verified_at",
            name="ck_capa_closure_date"
        ),
    )

# =====================================================
# 15. AUDIT EVENT TABLE
# =====================================================

class AuditEvent(Base):

    __tablename__ = "audit_events"

    event_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    entity_type = Column(String(50), nullable=False)

    entity_id = Column(String(50), nullable=False)

    event_type = Column(String(50), nullable=False)

    old_value = Column(String(5000), nullable=True)

    new_value = Column(String(5000), nullable=True)

    event_timestamp = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp()
    )

    performed_by = Column(String(100), nullable=False)

    reason = Column(String(1000), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('CREATED', 'UPDATED', 'STATUS_CHANGED', 'DELETED', 'VERIFIED', 'CLOSED')",
            name="ck_audit_event_type"
        ),
    )
