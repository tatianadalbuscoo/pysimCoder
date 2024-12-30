
import os
import sys
import unittest
from unittest.mock import mock_open, patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'CodeGen', 'templates')))
from delfino import dispatch_main_generation, generate_main_mode1_timer, generate_main_mode1_epwm, generate_main_mode2_timer, generate_main_mode2_epwm


"""

This script contains unit tests for the following functions from delfino.py:
- dispatch_main_generation
- generate_main_mode1_timer
- generate_main_mode1_epwm
- generate_main_mode2_timer
- generate_main_mode2_epwm:

It tests various functionalities including state-driven logic for main file generation, interrupt handling for timers and ePWM, and ADC triggering mechanisms.


- Test dispatch_main_generation function:  

    - test_dispatch_main_generation_state_1:        Test dispatch_main_generation with state=1 (Mode 1 with Timer).
                                                    Simulated Condition: The function is called with state=1, which corresponds to Mode 1 with Timer interrupts.

    - test_dispatch_main_generation_state_2:        Test dispatch_main_generation with state=2 (Mode 1 with ePWM).
                                                    Simulated Condition: The function is called with state=2, which corresponds to Mode 1 with ePWM interrupts.

    - test_dispatch_main_generation_state_3:        Test dispatch_main_generation with state=3 (Mode 2 with Timer and ADC).
                                                    Simulated Condition: The function is called with state=3, which corresponds to Mode 2 using Timer interrupts and ADC triggering.

    - test_dispatch_main_generation_state_4:        Test dispatch_main_generation with state=4 (Mode 2 with ePWM and ADC).
                                                    Simulated Condition: The function is called with state=4, which corresponds to Mode 2 using ePWM interrupts and ADC triggering.

    - test_dispatch_main_generation_invalid_state:  Test dispatch_main_generation with an invalid state.
                                                    Simulated Condition: The function is called with an invalid state (e.g., state=99), which is not handled by the function logic.

- Test generate_main_mode1_timer function:

    - test_generate_main_mode1_timer:               Test generate_main_mode1_timer by verifying the generated content line by line.
                                                    Simulated Condition: The function is provided with valid inputs to generate `main.c`.

- Test generate_main_mode1_epwm function:

    - test_generate_main_mode1_epwm:                Test generate_main_mode1_epwm by verifying the generated content line by line.
                                                    Simulated Condition: The function is provided with valid inputs to generate `main.c`.

- Test generate_main_mode2_timer function:

    - test_generate_main_mode2_timer:               Test generate_main_mode2_timer by verifying the generated content line by line.
                                                    Simulated Condition: The function is provided with valid inputs to generate `main.c`.

- Test generate_main_mode2_epwm function:

    - TestGenerateMainMode2Epwm:                    Test generate_main_mode2_epwm by verifying the generated content line by line.
                                                    Simulated Condition: The function is provided with valid inputs to generate `main.c`.

"""


#################################################################################################################################################
# Test dispatch_main_generation function
#################################################################################################################################################

class TestDispatchMainGeneration(unittest.TestCase):


    @patch("delfino.generate_main_mode1_timer")
    @patch("delfino.generate_main_mode1_epwm")
    @patch("delfino.generate_main_mode2_timer")
    @patch("delfino.generate_main_mode2_epwm")
    def test_dispatch_main_generation_state_1(self, mock_mode2_epwm, mock_mode2_timer, mock_mode1_epwm, mock_mode1_timer):

        """

        Test dispatch_main_generation with state=1 (Mode 1 with Timer).
        Simulated Condition: The function is called with state=1, which corresponds to Mode 1 with Timer interrupts.

        """

        dispatch_main_generation(
            state=1,
            path_main="path/to/main.c",
            model="exampleModel",
            timer_period=1000,
            tbprd=None,
            pwm_output=None,
            adc_block=None
        )

        # Verify that generate_main_mode1_timer is called once with the correct arguments. Expected: Success
        mock_mode1_timer.assert_called_once_with("path/to/main.c", "exampleModel", 1000)

        # Verify that generate_main_mode1_epwm is not called. Expected: No call
        mock_mode1_epwm.assert_not_called()

        # Verify that generate_main_mode2_timer is not called. Expected: No call
        mock_mode2_timer.assert_not_called()

        # Verify that generate_main_mode2_epwm is not called. Expected: No call
        mock_mode2_epwm.assert_not_called()


    @patch("delfino.generate_main_mode1_timer")
    @patch("delfino.generate_main_mode1_epwm")
    @patch("delfino.generate_main_mode2_timer")
    @patch("delfino.generate_main_mode2_epwm")
    def test_dispatch_main_generation_state_2(self, mock_mode2_epwm, mock_mode2_timer, mock_mode1_epwm, mock_mode1_timer):

        """

        Test dispatch_main_generation with state=2 (Mode 1 with ePWM).
        Simulated Condition: The function is called with state=2, which corresponds to Mode 1 with ePWM interrupts.

        """

        dispatch_main_generation(
            state=2,
            path_main="path/to/main.c",
            model="exampleModel",
            timer_period=None,
            tbprd=2000,
            pwm_output="out1a",
            adc_block=None
        )

        # Verify that generate_main_mode1_epwm is called once with the correct arguments. Expected: Success
        mock_mode1_epwm.assert_called_once_with("path/to/main.c", "exampleModel", 2000, "out1a")

        # Verify that generate_main_mode1_timer is not called. Expected: No call
        mock_mode1_timer.assert_not_called()

        # Verify that generate_main_mode2_timer is not called. Expected: No call
        mock_mode2_timer.assert_not_called()

        # Verify that generate_main_mode2_epwm is not called. Expected: No call
        mock_mode2_epwm.assert_not_called()


    @patch("delfino.generate_main_mode1_timer")
    @patch("delfino.generate_main_mode1_epwm")
    @patch("delfino.generate_main_mode2_timer")
    @patch("delfino.generate_main_mode2_epwm")
    def test_dispatch_main_generation_state_3(self, mock_mode2_epwm, mock_mode2_timer, mock_mode1_epwm, mock_mode1_timer):

        """

        Test dispatch_main_generation with state=3 (Mode 2 with Timer and ADC).
        Simulated Condition: The function is called with state=3, which corresponds to Mode 2 using Timer interrupts and ADC triggering.

        """

        adc_block = {"module": "A", "soc": 0, "channel": 3}
        dispatch_main_generation(
            state=3,
            path_main="path/to/main.c",
            model="exampleModel",
            timer_period=5000,
            tbprd=None,
            pwm_output=None,
            adc_block=adc_block
        )

        # Verify that generate_main_mode2_timer is called once with the correct arguments. Expected: Success
        mock_mode2_timer.assert_called_once_with("path/to/main.c", "exampleModel", 5000, adc_block)

        # Verify that generate_main_mode1_timer is not called. Expected: No call
        mock_mode1_timer.assert_not_called()

        # Verify that generate_main_mode1_epwm is not called. Expected: No call
        mock_mode1_epwm.assert_not_called()

        # Verify that generate_main_mode2_epwm is not called. Expected: No call
        mock_mode2_epwm.assert_not_called()


    @patch("delfino.generate_main_mode1_timer")
    @patch("delfino.generate_main_mode1_epwm")
    @patch("delfino.generate_main_mode2_timer")
    @patch("delfino.generate_main_mode2_epwm")
    def test_dispatch_main_generation_state_4(self, mock_mode2_epwm, mock_mode2_timer, mock_mode1_epwm, mock_mode1_timer):

        """

        Test dispatch_main_generation with state=4 (Mode 2 with ePWM and ADC).
        Simulated Condition: The function is called with state=4, which corresponds to Mode 2 using ePWM interrupts and ADC triggering.

        """

        adc_block = {"module": "B", "soc": 1, "channel": 5}
        dispatch_main_generation(
            state=4,
            path_main="path/to/main.c",
            model="exampleModel",
            timer_period=None,
            tbprd=4000,
            pwm_output="out2b",
            adc_block=adc_block
        )

        # Verify that generate_main_mode2_epwm is called once with the correct arguments. Expected: Success
        mock_mode2_epwm.assert_called_once_with("path/to/main.c", "exampleModel", 4000, "out2b", adc_block)

        # Verify that generate_main_mode1_timer is not called. Expected: No call
        mock_mode1_timer.assert_not_called()

        # Verify that generate_main_mode1_epwm is not called. Expected: No call
        mock_mode1_epwm.assert_not_called()

        # Verify that generate_main_mode2_timer is not called. Expected: No call
        mock_mode2_timer.assert_not_called()


    @patch("delfino.generate_main_mode1_timer")
    @patch("delfino.generate_main_mode1_epwm")
    @patch("delfino.generate_main_mode2_timer")
    @patch("delfino.generate_main_mode2_epwm")
    def test_dispatch_main_generation_invalid_state(self, mock_mode2_epwm, mock_mode2_timer, mock_mode1_epwm, mock_mode1_timer):

        """

        Test dispatch_main_generation with an invalid state.
        Simulated Condition: The function is called with an invalid state (e.g., state=99), which is not handled by the function logic.

        """

        with self.assertRaises(ValueError):
            dispatch_main_generation(
                state=99,
                path_main="path/to/main.c",
                model="exampleModel",
                timer_period=None,
                tbprd=None,
                pwm_output=None,
                adc_block=None
            )

        # Verify that generate_main_mode1_timer is not called. Expected: No call
        mock_mode1_timer.assert_not_called()

        # Verify that generate_main_mode1_epwm is not called. Expected: No call
        mock_mode1_epwm.assert_not_called()

        # Verify that generate_main_mode2_timer is not called. Expected: No call
        mock_mode2_timer.assert_not_called()

        # Verify that generate_main_mode2_epwm is not called. Expected: No call
        mock_mode2_epwm.assert_not_called()        


#################################################################################################################################################
# Test generate_main_mode1_timer function
#################################################################################################################################################

# State 1
class TestGenerateMainMode1Timer(unittest.TestCase):


    @patch("builtins.open", new_callable=mock_open)
    def test_generate_main_mode1_timer(self, mock_file):

        """

        Test generate_main_mode1_timer by verifying the generated content line by line.
        Simulated Condition: The function is provided with valid inputs to generate `main.c`.

        """

        # Input parameters
        path_main = "path/to/main.c"
        model = "exampleModel"
        timer_period = 1000

        expected_content = f"""//###########################################################################
            // FILE:   main.c
            // AUTHOR: Tatiana Dal Busco
            // DATE:   December 2024
            //###########################################################################

            #include "F28x_Project.h"

            void setup(void);
            double get_run_time(void);
            double get_Tsamp(void);
            __interrupt void cpu_timer0_isr(void);

            static double Tsamp = 0.001;  // Time range
            static double T = 0.0;         // Current time

            void main(void)
            {{
                setup();
                while (1) {{}}
            }}

            // CPU Timer 0 ISR: Handles periodic timer interrupts
            __interrupt void cpu_timer0_isr(void)
            {{
                CpuTimer0.InterruptCount++;
                T += Tsamp;
                {model}_isr(T);
                PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;
            }}

            // Sets up system control, peripherals, interrupts, and Timer 0 for the application
            void setup(void)
            {{

                // Initialize the system control: clock, PLL, and peripheral settings
                InitSysCtrl();

                // Initialize General Purpose Input/Output pins
                InitGpio();

                // Disable all CPU interrupts
                DINT;

                // Initialize the Peripheral Interrupt Expansion (PIE) control registers
                InitPieCtrl();

                // Clear all interrupt enable registers
                IER = 0x0000;

                // Clear all interrupt flag registers
                IFR = 0x0000;

                // Initialize the PIE vector table with default interrupt vectors
                InitPieVectTable();

                {model}_init();

                // Map the CPU Timer 0 interrupt to its ISR (Interrupt Service Routine)
                EALLOW;
                PieVectTable.TIMER0_INT = &cpu_timer0_isr;
                EDIS;

                // Initialize CPU Timers and configure Timer 0
                InitCpuTimers();
                ConfigCpuTimer(&CpuTimer0, 200, 1000);
                CpuTimer0Regs.TCR.all = 0x4000; // Start Timer 0

                // Enable CPU interrupt group 1
                IER |= M_INT1;

                // Enable PIE interrupt for Timer 0
                PieCtrlRegs.PIEIER1.bit.INTx7 = 1;

                // Enable global interrupts and real-time interrupts
                EINT;
                ERTM;

            }}

            // Returns the current runtime
            double get_run_time(void)
            {{
                return T;
            }}

            // Returns the sampling time interval
            double get_Tsamp(void)
            {{
                return Tsamp;
            }}

        """

        # Normalize content by stripping leading and trailing spaces
        expected_lines = [line.strip() for line in expected_content.splitlines()]

        generate_main_mode1_timer(path_main, model, timer_period)

        # Verify that the file is opened with the correct path and mode. Expected: Correct call
        mock_file.assert_called_once_with(path_main, "w")

        # Retrieve the written content from the mock
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Removes leading and trailing spaces from each line
        written_lines = [line.strip() for line in written_content.splitlines()]

        # Compare line by line
        for i, (expected_line, written_line) in enumerate(zip(expected_lines, written_lines), 1):
            with self.subTest(line=i):

                # Assert each line matches the expected output. Expected: Match Found
                self.assertEqual(written_line, expected_line, f"Mismatch at line {i}")
    

#################################################################################################################################################
# Test generate_main_mode1_epwm function
#################################################################################################################################################

# State 2
class TestGenerateMainMode1Epwm(unittest.TestCase):


    @patch("builtins.open", new_callable=mock_open)
    def test_generate_main_mode1_epwm(self, mock_file):

        """

        Test generate_main_mode1_epwm by verifying the generated content line by line.
        Simulated Condition: The function is provided with valid inputs to generate `main.c`.

        """

        # Input parameters
        path_main = "path/to/main.c"
        model = "exampleModel"
        tbprd = 5000
        pwm_output = "out1a"

        pwm_period = (2 * int(tbprd)) / 1e8
        number_epwm = "epwm1"
        number_epwm_capsLock = "EPWM1"
        number_epwm_digit = 1
        epwm_regs = "EPwm1Regs"

        expected_content = f"""//###########################################################################
            // FILE:   main.c
            // AUTHOR: Tatiana Dal Busco
            // DATE:   December 2024
            //###########################################################################

            #include "F28x_Project.h"

            void setup(void);
            double get_run_time(void);
            double get_Tsamp(void);
            __interrupt void {number_epwm}_isr(void);

            static double Tsamp = {pwm_period}; // Time range
            static double T = 0.0;         // Current time

            void main(void)
            {{
                setup();
                while (1) {{}}
            }}

            // ePWM1 Interrupt Service Routine
            __interrupt void {number_epwm}_isr(void)
            {{
                T += Tsamp;
                {model}_isr(T);

                // Clear the interrupt flag for ePWM
                {epwm_regs}.ETCLR.bit.INT = 1;

                // Acknowledge the interrupt in PIE
                PieCtrlRegs.PIEACK.all = PIEACK_GROUP3;
            }}

            // Sets up system control, peripherals, interrupts, and ePWM for the application
            void setup(void)
            {{

                // Initialize the system control: clock, PLL, and peripheral settings
                InitSysCtrl();

                // Initialize General Purpose Input/Output pins
                InitGpio();

                // Disable all CPU interrupts
                DINT;

                // Initialize the Peripheral Interrupt Expansion (PIE) control registers
                InitPieCtrl();

                // Clear all interrupt enable registers
                IER = 0x0000;

                // Clear all interrupt flag registers
                IFR = 0x0000;

                // Initialize the PIE vector table with default interrupt vectors
                InitPieVectTable();

                {model}_init();

                // Link ISR to ePWM1 interrupt
                EALLOW;
                PieVectTable.{number_epwm_capsLock}_INT = &{number_epwm}_isr;
                EDIS;

                // Enable ePWM interrupt in PIE group 3
                PieCtrlRegs.PIEIER3.bit.INTx{number_epwm_digit} = 1;

                // Enable CPU interrupt group 3
                IER |= M_INT3;

                // Enable global interrupts and real-time interrupts
                EINT;
                ERTM;

            }}

            // Returns the current runtime
            double get_run_time(void)
            {{
                return T;
            }}

            // Returns the sampling time interval
            double get_Tsamp(void)
            {{
                return Tsamp;
            }}

        """

        # Normalize content by stripping leading and trailing spaces
        expected_lines = [line.strip() for line in expected_content.splitlines()]

        generate_main_mode1_epwm(path_main, model, tbprd, pwm_output)

        # Verify that the file is opened with the correct path and mode. Expected: Correct call
        mock_file.assert_called_once_with(path_main, "w")

        # Retrieve the written content from the mock
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Removes leading and trailing spaces from each line
        written_lines = [line.strip() for line in written_content.splitlines()]

        # Compare line by line
        for i, (expected_line, written_line) in enumerate(zip(expected_lines, written_lines), 1):
            with self.subTest(line=i):

                # Assert each line matches the expected output. Expected: Match Found
                self.assertEqual(written_line, expected_line, f"Mismatch at line {i}")


#################################################################################################################################################
# Test generate_main_mode2_timer function
#################################################################################################################################################

# State 3
class TestGenerateMainMode2Timer(unittest.TestCase):


    @patch("builtins.open", new_callable=mock_open)
    def test_generate_main_mode2_timer(self, mock_file):

        """

        Test generate_main_mode2_timer by verifying the generated content line by line.
        Simulated Condition: The function is provided with valid inputs to generate `main.c`.

        """

        # Input parameters
        path_main = "path/to/main.c"
        model = "exampleModel"
        timer_period = 10000
        adc_block = {"module": "A", "soc": 0, "channel": 3}

        Tsamp = float(timer_period) / 1000000
        module = adc_block["module"]
        module_lower = module.lower()
        soc = int(adc_block["soc"])
        interrupt = "PieCtrlRegs.PIEIER1.bit.INTx1 = 1;"  # Specific to module A

        expected_content = f"""//###########################################################################
            // FILE:   main.c
            // AUTHOR: Tatiana Dal Busco
            // DATE:   December 2024
            //###########################################################################

            #include "F28x_Project.h"

            // Function Prototypes
            void setup(void);
            double get_run_time(void);
            double get_Tsamp(void);
            __interrupt void adc{module_lower}1_isr(void);
            __interrupt void cpu_timer0_isr(void);

            // Defines
            #define RESULTS_BUFFER_SIZE 256

            // Globals
            Uint16 AdcResults[RESULTS_BUFFER_SIZE];
            Uint16 resultsIndex = 0;
            volatile Uint16 bufferFull = 0;
            static double Tsamp = {Tsamp};  // Sample interval
            static double T = 0.0;       // Current time

            void main(void)
            {{
                setup();
                while (1)
                {{
                    if (bufferFull)
                    {{
                        bufferFull = 0;
                    }}
                }}
            }}

            // CPU Timer 0 ISR
            __interrupt void cpu_timer0_isr(void)
            {{
                CpuTimer0.InterruptCount++;

                // Force start ADC conversion (It must be the last one, compared to the other adcs)
                Adc{module_lower}Regs.ADCSOCFRC1.bit.SOC{soc} = 1;

                // Acknowledge interrupt in PIE
                PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;
            }}

            // ADC ISR
            __interrupt void adc{module_lower}1_isr(void)
            {{

                // Store ADC result in buffer
                AdcResults[resultsIndex++] = Adc{module_lower}ResultRegs.ADCRESULT{soc};
                if (resultsIndex >= RESULTS_BUFFER_SIZE)
                {{
                    resultsIndex = 0; // Reset the buffer index
                    bufferFull = 1;   // Set the buffer full flag
                }}

                // Clear ADC interrupt flag
                Adc{module_lower}Regs.ADCINTFLGCLR.bit.ADCINT1 = 1;

                T += Tsamp;
                {model}_isr(T);

                // Acknowledge the interrupt in PIE
                PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;
            }}

            // Sets up system control, peripherals, interrupts, and ePWM for the application
            void setup(void)
            {{

                // Initialize the system control: clock, PLL, and peripheral settings
                InitSysCtrl();

                // Initialize General Purpose Input/Output pins
                InitGpio();

                // Disable all CPU interrupts
                DINT;

                // Initialize the Peripheral Interrupt Expansion (PIE) control registers
                InitPieCtrl();

                // Clear all interrupt enable registers
                IER = 0x0000;

                // Clear all interrupt flag registers
                IFR = 0x0000;

                // Initialize the PIE vector table with default interrupt vectors
                InitPieVectTable();

                {model}_init();

                // Map ISRs to interrupt vectors
                EALLOW;
                PieVectTable.TIMER0_INT = &cpu_timer0_isr;
                PieVectTable.ADC{module}1_INT = &adc{module_lower}1_isr;
                EDIS;

                // Configure CPU Timer 0
                InitCpuTimers();
                ConfigCpuTimer(&CpuTimer0, 200, {timer_period});
                CpuTimer0Regs.TCR.all = 0x4000; // Start Timer 0

                // Enable PIE interrupts for Timer 0 and ADC
                IER |= M_INT1;                     // Enable CPU interrupt group 1
                PieCtrlRegs.PIEIER1.bit.INTx7 = 1; // Enable PIE interrupt for Timer 0
                {interrupt}                       // Enable PIE interrupt for ADC

                // Enable global and real-time interrupts
                EINT;
                ERTM;

            }}

            // Returns the current runtime
            double get_run_time(void)
            {{
                return T;
            }}

            // Returns the sampling time interval
            double get_Tsamp(void)
            {{
                return Tsamp;
            }}

        """

        # Normalize content by stripping leading and trailing spaces
        expected_lines = [line.strip() for line in expected_content.splitlines()]

        generate_main_mode2_timer(path_main, model, timer_period, adc_block)

        # Verify that the file is opened with the correct path and mode. Expected: Correct call
        mock_file.assert_called_once_with(path_main, "w")

        # Retrieve the written content from the mock
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Removes leading and trailing spaces from each line
        written_lines = [line.strip() for line in written_content.splitlines()]

        # Compare line by line
        for i, (expected_line, written_line) in enumerate(zip(expected_lines, written_lines), 1):
            with self.subTest(line=i):

                # Assert each line matches the expected output. Expected: Match Found
                self.assertEqual(written_line, expected_line, f"Mismatch at line {i}")


#################################################################################################################################################
# Test generate_main_mode2_epwm function
#################################################################################################################################################

# State 4
class TestGenerateMainMode2Epwm(unittest.TestCase):


    @patch("builtins.open", new_callable=mock_open)
    def test_generate_main_mode2_epwm(self, mock_file):

        """

        Test generate_main_mode2_epwm by verifying the generated content line by line.
        Simulated Condition: The function is provided with valid inputs to generate `main.c`.

        """

        # Input parameters
        path_main = "path/to/main.c"
        model = "exampleModel"
        tbprd = 2000
        pwm_output = "out1a"
        adc_block = {"module": "A", "soc": 0, "channel": 3}

        pwm_period = (2 * int(tbprd)) / 1e8
        epwmRegs = "EPwm1Regs"
        module = adc_block["module"]
        module_lower = module.lower()
        soc = int(adc_block["soc"])
        interrupt = "PieCtrlRegs.PIEIER1.bit.INTx1 = 1;"  # For module A

        expected_content = f"""//###########################################################################
            // FILE:   main.c
            // AUTHOR: Tatiana Dal Busco
            // DATE:   December 2024
            //###########################################################################

            #include "F28x_Project.h"

            // Function Prototypes
            void ConfigureADC(void);
            void SetupADCEpwm(Uint16 channel);
            void setup(void);
            void loop(void);
            double get_run_time(void);
            double get_Tsamp(void);
            interrupt void adc{module_lower}1_isr(void);

            // Defines
            #define RESULTS_BUFFER_SIZE 256

            // Globals
            Uint16 AdcResults[RESULTS_BUFFER_SIZE];
            Uint16 resultsIndex;
            volatile Uint16 bufferFull;
            static double Tsamp = {pwm_period}; // Time range
            static double T = 0.0;        // Current time

            void main(void)
            {{
                setup();
                loop();
            }}

            // adc{module_lower}1_isr - Read ADC Buffer in ISR
            // Everytime ADC complete a conversion, the value is memorized in the AdcResults buffer.
            interrupt void adc{module_lower}1_isr(void)
            {{

                // Store ADC result in buffer
                AdcResults[resultsIndex++] = Adc{module_lower}ResultRegs.ADCRESULT{soc};
                if(RESULTS_BUFFER_SIZE <= resultsIndex)
                {{
                    resultsIndex = 0; // Reset the buffer index
                    bufferFull = 1;   // Mark the buffer as full
                }}

                // Clear ADC interrupt flag
                Adc{module_lower}Regs.ADCINTFLGCLR.bit.ADCINT1 = 1;

                // Check if overflow has occurred
                if(1 == Adc{module_lower}Regs.ADCINTOVF.bit.ADCINT1)
                {{
                    Adc{module_lower}Regs.ADCINTOVFCLR.bit.ADCINT1 = 1; // Clear overflow flag
                    Adc{module_lower}Regs.ADCINTFLGCLR.bit.ADCINT1 = 1; // Clear interrupt flag
                }}

                T += Tsamp;
                {model}_isr(T);

                // Acknowledge interrupt in PIE
                PieCtrlRegs.PIEACK.all = PIEACK_GROUP1;
            }}

            // Sets up system control, peripherals, interrupts, and ePWM for the application
            void setup(void)
            {{

                // Initialize the system control: clock, PLL, and peripheral settings
                InitSysCtrl();

                // Initialize General Purpose Input/Output pins
                InitGpio();

                // Disable all CPU interrupts
                DINT;

                // Initialize the Peripheral Interrupt Expansion (PIE) control registers
                InitPieCtrl();

                // Clear all interrupt enable registers
                IER = 0x0000;

                // Clear all interrupt flag registers
                IFR = 0x0000;

                // Initialize the PIE vector table with default interrupt vectors
                InitPieVectTable();

                // Map the ADC ISR to the interrupt vector
                EALLOW;
                PieVectTable.ADC{module}1_INT = &adc{module_lower}1_isr;
                EDIS;

                // Configure ePWM for ADC triggering
                EALLOW;
                {epwmRegs}.ETSEL.bit.SOCAEN = 0; // Disable SOC
                {epwmRegs}.ETSEL.bit.SOCASEL = 6;// Select SOC on up-down count
                {epwmRegs}.ETPS.bit.SOCAPRD = 1; // Generate pulse on 1st event
                EDIS;

                {model}_init();

                EALLOW;
                {epwmRegs}.TBCTL.bit.CTRMODE = 3; // freeze counter
                EDIS;

                // Enable global and real-time interrupts
                IER |= M_INT1;
                EINT;
                ERTM;

                // Initialize the ADC results buffer
                for(resultsIndex = 0; resultsIndex < RESULTS_BUFFER_SIZE; resultsIndex++)
                {{
                    AdcResults[resultsIndex] = 0;
                }}
                resultsIndex = 0; // Reset buffer index
                bufferFull = 0;   // Reset buffer full flag

                // Enable PIE interrupt for ADC
                {interrupt}

                // Enable Time Base Clock Sync
                EALLOW;
                CpuSysRegs.PCLKCR0.bit.TBCLKSYNC = 1;
                EDIS;

            }}

            // Main loop - Continuously processes ADC conversions
            void loop(void)
            {{

                do
                {{

                    // Start ePWM for ADC triggering
                    {epwmRegs}.ETSEL.bit.SOCAEN = 1;
                    {epwmRegs}.TBCTL.bit.CTRMODE = 2; // Set ePWM counter to up-down mode

                    // Wait until the buffer is full
                    while(!bufferFull);
                    bufferFull = 0; // Reset buffer full flag

                    // Stop ePWM
                    {epwmRegs}.ETSEL.bit.SOCAEN = 0;  // Disable SOC
                    {epwmRegs}.TBCTL.bit.CTRMODE = 3; // Freeze ePWM counter

                    // At this point, AdcResults[] contains ADC conversion results

                }} while(1);
            }}

            // Returns the current runtime
            double get_run_time(void)
            {{
                return T;
            }}

            // Returns the sampling time interval
            double get_Tsamp(void)
            {{
                return Tsamp;
            }}

        """

        # Normalize content by stripping leading and trailing spaces
        expected_lines = [line.strip() for line in expected_content.splitlines()]

        generate_main_mode2_epwm(path_main, model, tbprd, pwm_output, adc_block)

        # Verify that the file is opened with the correct path and mode. Expected: Correct call
        mock_file.assert_called_once_with(path_main, "w")

        # Retrieve the written content from the mock
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Removes leading and trailing spaces from each line
        written_lines = [line.strip() for line in written_content.splitlines()]

        # Compare line by line
        for i, (expected_line, written_line) in enumerate(zip(expected_lines, written_lines), 1):
            with self.subTest(line=i):

                # Assert each line matches the expected output. Expected: Match Found
                self.assertEqual(written_line, expected_line, f"Mismatch at line {i}")


if __name__ == "__main__":
    unittest.main()
