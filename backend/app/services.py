"""
Services module for AgentCores - Updated for new User model
Provides business logic for tenant management, user operations, and security
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.database import (
    InvitationStatus,
    SecurityEvent,
    Tenant,
    TenantInvitation,
    User,
    UserRole,
)


class TenantService:
    """Service for tenant management operations"""

    @staticmethod
    def get_tenant_by_id(db: Session, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()

    @staticmethod
    def get_tenant_users(db: Session, tenant_id: str) -> List[User]:
        """Get all users for a tenant"""
        return (
            db.query(User)
            .filter(User.tenant_id == tenant_id, User.is_active.is_(True))
            .all()
        )

    @staticmethod
    def get_tenant_stats(db: Session, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive tenant statistics"""
        tenant = TenantService.get_tenant_by_id(db, tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")

        # User statistics
        total_users = db.query(User).filter(User.tenant_id == tenant_id).count()
        active_users = (
            db.query(User)
            .filter(User.tenant_id == tenant_id, User.is_active.is_(True))
            .count()
        )

        # Role distribution
        role_distribution = {}
        for role in UserRole:
            count = (
                db.query(User)
                .filter(User.tenant_id == tenant_id, User.role == role)
                .count()
            )
            role_distribution[role.value] = count

        # Recent activity (last 24 hours)
        recent_logins = (
            db.query(User)
            .filter(
                User.tenant_id == tenant_id,
                User.last_login >= datetime.utcnow() - timedelta(hours=24),
            )
            .count()
        )

        # Security events (last 7 days)
        recent_events = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.tenant_id == tenant_id,
                SecurityEvent.created_at >= datetime.utcnow() - timedelta(days=7),
            )
            .count()
        )

        return {
            "tenant_info": {
                "id": tenant.id,
                "name": tenant.name,
                "status": tenant.status.value,
                "tier": tenant.tier.value,
                "domain": tenant.domain,
            },
            "user_stats": {
                "total_users": total_users,
                "active_users": active_users,
                "role_distribution": role_distribution,
            },
            "activity_stats": {
                "recent_logins_24h": recent_logins,
                "security_events_7d": recent_events,
            },
            "resource_usage": {
                "current_agents": tenant.current_agents,
                "max_agents": tenant.max_agents,
                "current_month_tasks": tenant.current_month_tasks,
                "current_month_cost": tenant.current_month_cost,
                "max_monthly_cost": tenant.max_monthly_cost,
            },
        }


class UserService:
    """Service for user management operations"""

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(
        db: Session, email: str, tenant_id: Optional[str] = None
    ) -> Optional[User]:
        """Get user by email, optionally filtered by tenant"""
        query = db.query(User).filter(User.email == email)
        if tenant_id:
            query = query.filter(User.tenant_id == tenant_id)
        return query.first()

    @staticmethod
    def create_user(
        db: Session,
        tenant_id: str,
        email: str,
        first_name: str,
        last_name: str,
        password_hash: str,
        role: UserRole,
        department: Optional[str] = None,
        job_title: Optional[str] = None,
    ) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, email, tenant_id)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            )

        user = User(
            tenant_id=tenant_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            role=role,
            department=department,
            job_title=job_title,
            is_active=True,
            is_verified=False,
            timezone="UTC",
            language="en",
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user_role(
        db: Session, user_id: str, new_role: UserRole, updated_by: str
    ) -> User:
        """Update user role"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        old_role = user.role
        setattr(user, "role", new_role)
        user.updated_at = datetime.utcnow()

        # Log the role change as a security event
        SecurityService.log_security_event(
            db=db,
            tenant_id=user.tenant_id,
            user_id=updated_by,
            event_type="role_change",
            severity="info",
            event_data={
                "target_user_id": user_id,
                "target_user_email": user.email,
                "old_role": old_role.value,
                "new_role": new_role.value,
            },
            result="success",
        )

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate_user(db: Session, user_id: str, deactivated_by: str) -> User:
        """Deactivate a user"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        setattr(user, "is_active", False)
        user.updated_at = datetime.utcnow()

        # Log the deactivation
        SecurityService.log_security_event(
            db=db,
            tenant_id=user.tenant_id,
            user_id=deactivated_by,
            event_type="user_deactivated",
            severity="info",
            event_data={"target_user_id": user_id, "target_user_email": user.email},
            result="success",
        )

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_last_activity(db: Session, user_id: str):
        """Update user's last activity timestamp"""
        user = UserService.get_user_by_id(db, user_id)
        if user:
            setattr(user, "last_activity", datetime.utcnow())
            db.commit()


class SecurityService:
    """Service for security operations and monitoring"""

    @staticmethod
    def log_security_event(
        db: Session,
        tenant_id: str,
        event_type: str,
        severity: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        event_data: Optional[Dict] = None,
        result: Optional[str] = None,
        risk_score: int = 0,
        threat_indicators: Optional[List[str]] = None,
    ) -> SecurityEvent:
        """Log a security event"""
        event = SecurityEvent(
            tenant_id=tenant_id,
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            ip_address=ip_address,
            user_agent=user_agent,
            event_data=event_data or {},
            result=result,
            risk_score=risk_score,
            threat_indicators=threat_indicators or [],
        )

        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def get_security_dashboard_data(db: Session, tenant_id: str) -> Dict[str, Any]:
        """Get security dashboard data"""
        now = datetime.utcnow()

        # Total events in last 24 hours
        events_24h = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.tenant_id == tenant_id,
                SecurityEvent.created_at >= now - timedelta(hours=24),
            )
            .count()
        )

        # High risk events in last 24 hours
        high_risk_events = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.tenant_id == tenant_id,
                SecurityEvent.created_at >= now - timedelta(hours=24),
                SecurityEvent.risk_score >= 70,
            )
            .count()
        )

        # Failed login attempts in last 24 hours
        failed_logins = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.tenant_id == tenant_id,
                SecurityEvent.created_at >= now - timedelta(hours=24),
                SecurityEvent.event_type == "failed_login",
            )
            .count()
        )

        # Active users (logged in within last 24 hours)
        active_users = (
            db.query(User)
            .filter(
                User.tenant_id == tenant_id,
                User.last_login >= now - timedelta(hours=24),
            )
            .count()
        )

        # Recent security events
        recent_events = (
            db.query(SecurityEvent)
            .filter(SecurityEvent.tenant_id == tenant_id)
            .order_by(SecurityEvent.created_at.desc())
            .limit(10)
            .all()
        )

        # Event type distribution (last 7 days)
        event_types = (
            db.query(
                SecurityEvent.event_type, func.count(SecurityEvent.id).label("count")
            )
            .filter(
                SecurityEvent.tenant_id == tenant_id,
                SecurityEvent.created_at >= now - timedelta(days=7),
            )
            .group_by(SecurityEvent.event_type)
            .all()
        )

        return {
            "summary": {
                "total_events_24h": events_24h,
                "high_risk_events_24h": high_risk_events,
                "failed_logins_24h": failed_logins,
                "active_users_24h": active_users,
            },
            "recent_events": [
                {
                    "id": event.id,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "user_email": event.user.email if event.user else None,
                    "ip_address": event.ip_address,
                    "risk_score": event.risk_score,
                    "created_at": event.created_at.isoformat(),
                    "result": event.result,
                }
                for event in recent_events
            ],
            "event_type_distribution": {
                event_type: count for event_type, count in event_types
            },
        }

    @staticmethod
    def get_security_audit_data(db: Session, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive security audit data"""
        now = datetime.utcnow()

        # User access patterns
        user_logins = (
            db.query(
                User.email,
                User.role,
                func.count(SecurityEvent.id).label("login_count"),
                func.max(SecurityEvent.created_at).label("last_login"),
            )
            .join(SecurityEvent, User.id == SecurityEvent.user_id)
            .filter(
                User.tenant_id == tenant_id,
                SecurityEvent.event_type == "login",
                SecurityEvent.created_at >= now - timedelta(days=30),
            )
            .group_by(User.email, User.role)
            .all()
        )

        # Failed login attempts by IP
        failed_login_ips = (
            db.query(
                SecurityEvent.ip_address,
                func.count(SecurityEvent.id).label("attempt_count"),
                func.max(SecurityEvent.created_at).label("last_attempt"),
            )
            .filter(
                SecurityEvent.tenant_id == tenant_id,
                SecurityEvent.event_type == "failed_login",
                SecurityEvent.created_at >= now - timedelta(days=7),
            )
            .group_by(SecurityEvent.ip_address)
            .order_by(func.count(SecurityEvent.id).desc())
            .limit(20)
            .all()
        )

        # Permission violations
        permission_violations = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.tenant_id == tenant_id,
                SecurityEvent.event_type == "permission_denied",
                SecurityEvent.created_at >= now - timedelta(days=30),
            )
            .order_by(SecurityEvent.created_at.desc())
            .limit(50)
            .all()
        )

        # Risk score trends (last 7 days)
        risk_trends = (
            db.query(
                func.date(SecurityEvent.created_at).label("date"),
                func.avg(SecurityEvent.risk_score).label("avg_risk_score"),
                func.max(SecurityEvent.risk_score).label("max_risk_score"),
            )
            .filter(
                SecurityEvent.tenant_id == tenant_id,
                SecurityEvent.created_at >= now - timedelta(days=7),
            )
            .group_by(func.date(SecurityEvent.created_at))
            .all()
        )

        return {
            "user_access_patterns": [
                {
                    "email": email,
                    "role": role.value,
                    "login_count": login_count,
                    "last_login": last_login.isoformat() if last_login else None,
                }
                for email, role, login_count, last_login in user_logins
            ],
            "failed_login_attempts": [
                {
                    "ip_address": ip_address,
                    "attempt_count": attempt_count,
                    "last_attempt": last_attempt.isoformat(),
                }
                for ip_address, attempt_count, last_attempt in failed_login_ips
            ],
            "permission_violations": [
                {
                    "user_email": violation.user.email if violation.user else "Unknown",
                    "event_data": violation.event_data,
                    "ip_address": violation.ip_address,
                    "created_at": violation.created_at.isoformat(),
                }
                for violation in permission_violations
            ],
            "risk_score_trends": [
                {
                    "date": date.isoformat(),
                    "avg_risk_score": float(avg_risk_score) if avg_risk_score else 0,
                    "max_risk_score": max_risk_score or 0,
                }
                for date, avg_risk_score, max_risk_score in risk_trends
            ],
        }


class InvitationService:
    """Service for managing tenant invitations"""

    @staticmethod
    def create_invitation(
        db: Session,
        tenant_id: str,
        email: str,
        role: UserRole,
        invited_by: str,
        expires_in_days: int = 7,
    ) -> TenantInvitation:
        """Create a new tenant invitation"""
        # Check if user already exists
        existing_user = UserService.get_user_by_email(db, email, tenant_id)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="User already exists in this tenant"
            )

        # Check for existing pending invitation
        existing_invitation = (
            db.query(TenantInvitation)
            .filter(
                TenantInvitation.tenant_id == tenant_id,
                TenantInvitation.email == email,
                TenantInvitation.status == InvitationStatus.PENDING,
            )
            .first()
        )

        if existing_invitation:
            raise HTTPException(
                status_code=400,
                detail="Pending invitation already exists for this email",
            )

        invitation = TenantInvitation(
            tenant_id=tenant_id,
            email=email,
            role=role,
            invited_by=invited_by,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
            token=str(uuid.uuid4()),
        )

        db.add(invitation)
        db.commit()
        db.refresh(invitation)

        # Log the invitation
        SecurityService.log_security_event(
            db=db,
            tenant_id=tenant_id,
            user_id=invited_by,
            event_type="user_invited",
            severity="info",
            event_data={
                "invited_email": email,
                "invited_role": role.value,
                "invitation_id": invitation.id,
            },
            result="success",
        )

        return invitation

    @staticmethod
    def accept_invitation(
        db: Session, token: str, first_name: str, last_name: str, password_hash: str
    ) -> User:
        """Accept a tenant invitation and create user account"""
        invitation = (
            db.query(TenantInvitation)
            .filter(
                TenantInvitation.token == token,
                TenantInvitation.status == InvitationStatus.PENDING,
                TenantInvitation.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if not invitation:
            raise HTTPException(status_code=400, detail="Invalid or expired invitation")

        # Create the user
        user = UserService.create_user(
            db=db,
            tenant_id=invitation.tenant_id,
            email=str(invitation.email),
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            role=getattr(invitation, "role", UserRole.VIEWER),
        )

        # Mark invitation as accepted
        setattr(invitation, "status", InvitationStatus.ACCEPTED)
        setattr(invitation, "accepted_at", datetime.utcnow())
        invitation.accepted_by = user.id

        db.commit()

        return user
