# Discord RPC Test Module
# Simple tests to verify Discord RPC functionality

init python:
    def test_discord_rpc_basic():
        """Test basic Discord RPC functionality"""
        print("=== Discord RPC Basic Test ===")
        
        try:
            # Test status retrieval
            status = discord_rpc.get_status()
            print(f"Current status: {status}")
            
            # Test status info
            info = discord_rpc.get_status_info()
            print(f"Status info: {info}")
            
            # Test enable/disable
            print("Testing enable/disable...")
            discord_rpc.disable()
            print(f"After disable: {discord_rpc.get_status()}")
            
            discord_rpc.enable()
            print(f"After enable: {discord_rpc.get_status()}")
            
            print("=== Basic Test Complete ===")
            return True
            
        except Exception as e:
            print(f"Basic test failed: {e}")
            return False
    
    def test_discord_rpc_api():
        """Test Discord RPC API functions"""
        print("=== Discord RPC API Test ===")
        
        try:
            # Test API functions
            print("Testing API functions...")
            
            discord_set_main_menu()
            print("✓ discord_set_main_menu()")
            
            discord_set_in_game("Test Chapter", "Test Character")
            print("✓ discord_set_in_game()")
            
            discord_set_dialogue("Test Character", "Test Scene")
            print("✓ discord_set_dialogue()")
            
            discord_set_menu("Test Menu")
            print("✓ discord_set_menu()")
            
            discord_set_paused()
            print("✓ discord_set_paused()")
            
            discord_set_loading()
            print("✓ discord_set_loading()")
            
            discord_set_custom("Test State", "Test Details")
            print("✓ discord_set_custom()")
            
            # Test advanced API
            if 'drpc' in globals():
                drpc.set_with_timestamp("Test with timestamp", start_time=1234567890)
                print("✓ drpc.set_with_timestamp()")
            
            print("=== API Test Complete ===")
            return True
            
        except Exception as e:
            print(f"API test failed: {e}")
            return False
    
    def test_discord_rpc_settings():
        """Test Discord RPC settings functionality"""
        print("=== Discord RPC Settings Test ===")
        
        try:
            # Test settings functions
            print("Testing settings functions...")
            
            # Save original settings
            original_enabled = persistent.discord_rpc_enabled
            original_client_id = persistent.discord_rpc_client_id
            
            # Test toggle
            toggle_discord_rpc()
            print("✓ toggle_discord_rpc()")
            
            # Test settings application
            apply_discord_rpc_settings()
            print("✓ apply_discord_rpc_settings()")
            
            # Test reconnect
            discord_rpc_reconnect()
            print("✓ discord_rpc_reconnect()")
            
            # Restore original settings
            persistent.discord_rpc_enabled = original_enabled
            persistent.discord_rpc_client_id = original_client_id
            
            print("=== Settings Test Complete ===")
            return True
            
        except Exception as e:
            print(f"Settings test failed: {e}")
            return False
    
    def test_discord_rpc_reliability():
        """Test Discord RPC reliability features"""
        print("=== Discord RPC Reliability Test ===")
        
        try:
            # Test error handling
            print("Testing error handling...")
            
            if 'reliable_discord_rpc' in globals() and reliable_discord_rpc:
                # Test safe update
                result = reliable_discord_rpc.safe_update(
                    state="Test State",
                    details="Test Details"
                )
                print(f"✓ safe_update() result: {result}")
                
                # Test safe connect
                result = reliable_discord_rpc.safe_connect()
                print(f"✓ safe_connect() result: {result}")
            
            # Test error info
            error_info = get_discord_error_info()
            print(f"✓ get_discord_error_info(): {error_info}")
            
            print("=== Reliability Test Complete ===")
            return True
            
        except Exception as e:
            print(f"Reliability test failed: {e}")
            return False
    
    def run_all_discord_rpc_tests():
        """Run all Discord RPC tests"""
        print("\n" + "="*50)
        print("STARTING DISCORD RPC TESTS")
        print("="*50)
        
        tests = [
            ("Basic Functionality", test_discord_rpc_basic),
            ("API Functions", test_discord_rpc_api),
            ("Settings", test_discord_rpc_settings),
            ("Reliability", test_discord_rpc_reliability)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\nRunning {test_name} test...")
            try:
                result = test_func()
                results.append((test_name, result))
                print(f"{test_name}: {'PASS' if result else 'FAIL'}")
            except Exception as e:
                print(f"{test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        print("\n" + "="*50)
        print("TEST RESULTS SUMMARY")
        print("="*50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nTotal: {passed}/{total} tests passed")
        print("="*50)
        
        return passed == total

# Test screen for manual testing
screen discord_rpc_test_screen():
    """Test screen for Discord RPC functionality"""
    
    modal True
    zorder 200
    
    style_prefix "confirm"
    
    add "#000000aa"
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 800
        ysize 600
        
        vbox:
            spacing 20
            xfill True
            
            label "Discord RPC Test Panel" xalign 0.5
            
            hbox:
                spacing 20
                
                vbox:
                    spacing 10
                    text "Basic Tests:"
                    textbutton "Run All Tests" action Function(run_all_discord_rpc_tests)
                    textbutton "Basic Test" action Function(test_discord_rpc_basic)
                    textbutton "API Test" action Function(test_discord_rpc_api)
                    textbutton "Settings Test" action Function(test_discord_rpc_settings)
                    textbutton "Reliability Test" action Function(test_discord_rpc_reliability)
                
                vbox:
                    spacing 10
                    text "Manual Tests:"
                    textbutton "Set Main Menu" action Function(discord_set_main_menu)
                    textbutton "Set In Game" action Function(discord_set_in_game, "Test Chapter", "Test Character")
                    textbutton "Set Dialogue" action Function(discord_set_dialogue, "Test Character")
                    textbutton "Set Paused" action Function(discord_set_paused)
                    textbutton "Set Custom" action Function(discord_set_custom, "Test State", "Test Details")
                    textbutton "Clear Status" action Function(discord_clear)
            
            text "Current Status: [discord_rpc.get_status()]"
            
            if discord_rpc.last_error:
                text "Last Error: [discord_rpc.last_error]" color "#ff0000"
            
            hbox:
                spacing 20
                xalign 0.5
                
                textbutton "Close" action Return()
                textbutton "Open Settings" action ShowMenu("discord_rpc_settings")

# Add test option to main menu (for development)
init python:
    def add_test_to_main_menu():
        """Add test option to main menu for development"""
        # This can be called to add test option to main menu
        pass
