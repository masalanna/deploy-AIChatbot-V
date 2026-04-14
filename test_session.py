"""
Test script for conversation session management
"""

import qanstest

def test_session_management():
    """Test the new session management features"""
    
    print("=" * 60)
    print("Testing Conversation Session Management")
    print("=" * 60)
    
    # Test with a session ID
    session_id = "test_user_123"
    
    # Test 1: First question
    print("\n Test 1: First technical question")
    print("-" * 60)
    response1 = qanstest.get_qan_answer("What is Softdel?", session_id)
    print(f"Response: {response1[:200]}...")
    
    # Check session info
    session_info = qanstest.get_session_info(session_id)
    print(f"\nSession Info: {session_info}")
    
    # Test 2: Second question
    print("\n\nTest 2: Second technical question")
    print("-" * 60)
    response2 = qanstest.get_qan_answer("What are Softdel's IoT solutions?", session_id)
    print(f"Response: {response2[:200]}...")
    
    session_info = qanstest.get_session_info(session_id)
    print(f"\nSession Info: {session_info}")
    
    # Test 3: Third question
    print("\n\nTest 3: Third technical question")
    print("-" * 60)
    response3 = qanstest.get_qan_answer("Tell me about BACnet", session_id)
    print(f"Response: {response3[:200]}...")
    
    session_info = qanstest.get_session_info(session_id)
    print(f"\nSession Info: {session_info}")
    
    # Test 4-6: More questions to trigger 5th question prompt
    questions = [
        "What is EdificeEdge?",
        "Tell me about smart buildings",
        "What cloud services does Softdel use?"
    ]
    
    for i, question in enumerate(questions, 4):
        print(f"\n\nTest {i}: Technical question #{i}")
        print("-" * 60)
        response = qanstest.get_qan_answer(question, session_id)
        print(f"Response: {response[:300]}...")
        
        session_info = qanstest.get_session_info(session_id)
        print(f"\nSession Info: {session_info}")
        
        if "📞 Since you've shown interest" in response:
            print("\n✅ 5th question scheduling prompt detected!")
    
    # Test casual greeting (should not increment question count)
    print("\n\nTest: Casual greeting")
    print("-" * 60)
    response_casual = qanstest.get_qan_answer("Hi", session_id)
    print(f"Response: {response_casual}")
    
    session_info = qanstest.get_session_info(session_id)
    print(f"\nSession Info after greeting: {session_info}")
    
    # Test pricing query
    print("\n\nTest: Pricing query")
    print("-" * 60)
    response_pricing = qanstest.get_qan_answer("How much does it cost?", session_id)
    print(f"Response: {response_pricing[:200]}...")
    
    session_info = qanstest.get_session_info(session_id)
    print(f"\nFinal Session Info: {session_info}")
    
    # Clear session
    print("\n\nClearing session...")
    cleared = qanstest.clear_session(session_id)
    print(f"Session cleared: {cleared}")
    
    session_info_after_clear = qanstest.get_session_info(session_id)
    print(f"Session Info after clear: {session_info_after_clear}")
    
    print("\n" + "=" * 60)
    print("Session Management Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_session_management()
