# app/services/call_processor.py
"""Service for processing call events."""
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Call
from app.utils.helpers import get_param, determine_phone_type
from app.config import logger


async def process_event(params: Dict[str, Any], session: AsyncSession):
    """
    Process a phone event and update the calls table accordingly.
    
    Args:
        params: Dictionary of query parameters
        session: Database session
    """
    # Determine phone type
    phone_type = determine_phone_type(params)
    
    if phone_type == "unknown":
        logger.warning(f"Unknown phone type: {params}")
        return
    
    # Extract common parameters based on phone type
    event = get_param(params, "event")
    
    if phone_type == "yealink":
        phone_mac = get_param(params, "phone")
        call_id = get_param(params, "callid")
        number = get_param(params, "number")
        remote_number = get_param(params, "remotenumber", number)
    else:  # Cisco
        phone_mac = get_param(params, "mac")
        call_id = get_param(params, "callid")
        number = get_param(params, "number")
        remote_number = number
    
    # If call_id is unknown, generate one from phone_mac and timestamp
    if call_id == "unknown":
        call_id = f"{phone_mac}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Fetch existing call if it exists
    result = await session.execute(
        select(Call).filter(Call.call_id == call_id)
    )
    existing_call = result.scalars().first()
    
    # Process based on event type
    await _handle_event(
        event=event,
        existing_call=existing_call,
        call_id=call_id,
        phone_mac=phone_mac,
        remote_number=remote_number,
        phone_type=phone_type,
        params=params,
        session=session
    )


async def _handle_event(
    event: str,
    existing_call: Call,
    call_id: str,
    phone_mac: str,
    remote_number: str,
    phone_type: str,
    params: Dict[str, Any],
    session: AsyncSession
):
    """
    Handle different event types.
    
    Args:
        event: Event type
        existing_call: Existing call record if found
        call_id: Call ID
        phone_mac: Phone MAC address
        remote_number: Remote number
        phone_type: Phone type (yealink or cisco)
        params: Dictionary of query parameters
        session: Database session
    """
    # Call start events
    if event in ["call-start", "incoming-call"]:
        await _handle_call_start(
            event=event,
            existing_call=existing_call,
            call_id=call_id,
            phone_mac=phone_mac,
            remote_number=remote_number,
            session=session
        )
    
    # Call answer/established events
    elif event in ["call-established", "call-connected"]:
        await _handle_call_established(
            existing_call=existing_call,
            call_id=call_id,
            session=session
        )
    
    # Call end events
    elif event in ["call-end"]:
        await _handle_call_end(
            existing_call=existing_call,
            call_id=call_id,
            params=params,
            session=session
        )
    
    # Call hold events
    elif event in ["hold", "call-hold"]:
        await _handle_call_hold(
            existing_call=existing_call,
            call_id=call_id,
            session=session
        )
    
    # Call resume events
    elif event in ["resume", "call-resume"]:
        await _handle_call_resume(
            existing_call=existing_call,
            call_id=call_id,
            session=session
        )
    
    # Call transfer events
    elif event in ["transfer", "call-transfer", "attended-transfer"]:
        await _handle_call_transfer(
            existing_call=existing_call,
            call_id=call_id,
            phone_type=phone_type,
            params=params,
            session=session
        )


async def _handle_call_start(
    event: str,
    existing_call: Call,
    call_id: str,
    phone_mac: str,
    remote_number: str,
    session: AsyncSession
):
    """Handle call start events."""
    if not existing_call:
        direction = "incoming" if event == "incoming-call" else "outgoing"
        
        # For outgoing calls, from = phone, to = dialed number
        # For incoming calls, from = caller, to = phone
        from_number = phone_mac if direction == "outgoing" else remote_number
        to_number = remote_number if direction == "outgoing" else phone_mac
        
        # Create new call record
        new_call = Call(
            call_id=call_id,
            from_number=from_number,
            to_number=to_number,
            phone_mac=phone_mac,
            direction=direction,
            status='in_progress'
        )
        session.add(new_call)
        await session.commit()
        logger.info(f"New call started: {call_id}, Direction: {direction}")


async def _handle_call_established(
    existing_call: Call,
    call_id: str,
    session: AsyncSession
):
    """Handle call established events."""
    if existing_call:
        existing_call.status = "answered"
        await session.commit()
        logger.info(f"Call answered: {call_id}")


async def _handle_call_end(
    existing_call: Call,
    call_id: str,
    params: Dict[str, Any],
    session: AsyncSession
):
    """Handle call end events."""
    if existing_call:
        # Get duration from parameter or calculate
        duration_param = get_param(params, "duration", "0")
        try:
            duration = int(duration_param)
        except (ValueError, TypeError):
            # Calculate duration from started time if available
            if existing_call.started:
                start_time = existing_call.started
                duration = int((datetime.now() - start_time).total_seconds())
            else:
                duration = 0
        
        # Determine if call was successful
        status = "successful" if (existing_call.status == "answered" or duration > 5) else "unsuccessful"
        
        existing_call.finished = datetime.now()
        existing_call.total_duration = duration
        existing_call.status = status
        await session.commit()
        
        logger.info(f"Call ended: {call_id}, Duration: {duration}s, Status: {status}")


async def _handle_call_hold(
    existing_call: Call,
    call_id: str,
    session: AsyncSession
):
    """Handle call hold events."""
    if existing_call:
        existing_call.status = "on_hold"
        await session.commit()
        logger.info(f"Call on hold: {call_id}")


async def _handle_call_resume(
    existing_call: Call,
    call_id: str,
    session: AsyncSession
):
    """Handle call resume events."""
    if existing_call:
        existing_call.status = "answered"
        await session.commit()
        logger.info(f"Call resumed: {call_id}")


async def _handle_call_transfer(
    existing_call: Call,
    call_id: str,
    phone_type: str,
    params: Dict[str, Any],
    session: AsyncSession
):
    """Handle call transfer events."""
    if existing_call:
        # Extract transfer destination if available
        transfer_to = get_param(params, "transfer_to", "unknown")
        if phone_type == "cisco":  # Cisco uses different parameter
            transfer_to = get_param(params, "transfer", "unknown")
        
        logger.info(f"Call transferred: {call_id} to {transfer_to}")
        
        # Initialize transfers list if it doesn't exist
        if existing_call.transfers is None:
            existing_call.transfers = []
        
        # Add the transfer destination to the transfers list
        existing_call.transfers.append(transfer_to)
        
        # Commit the changes to the database
        await session.commit()

