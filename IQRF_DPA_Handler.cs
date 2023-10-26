using System;
using System.Collections.Generic;
using System.Collections;
using System.Text;

namespace IQRF_DPA_Handler
{
    
    ///<summary>
    ///DPA RX class
    ///</summary>
    ///<remarks>
    ///This class handles RX performance of DPA Protol
    ///</remarks>
    class DPA_RX
    {

        public enum DPA_RX_STATE
        {
            DPA_RX_NOERR,       // default state
            DPA_RX_OK,          // OK, message parsed
            DPA_RX_FE,          // Frame error
            DPA_RX_CRCERR       // CRC error
        }

        public UInt16 NADR;             // Node address
        public byte PNUM;               // Peripheral number
        public byte PCMD;               // Peripheral command
        public UInt16 HWPID;            // Hardware profile ID
        public byte[] Data;             // DPA Data
        public byte DLEN;               // DPA Data length
        public byte ErrN;               // Error number
        public byte DpaValue;

        private bool HDLC_CE;           // control escape flag
        private byte CRC;               // HDLC CRC
        public ArrayList Buffer;        // Input buffer

        public const byte HDLC_FLAG_SEQUENCE = 0x7e;    // Flag sequence constant
        public const byte HDLC_CONTROL_ESCAPE = 0x7d;   // Control escape constant
        public const byte HDLC_ESCAPE_BIT = 0x20;       // Escape bit constant
        public const byte HDLC_MIN_LEN = 0x0B;          // Minimum length of response
        public const byte HDLC_MAX_LEN = 0x80;          // Maximum length of buffer


        // Constructor
        public DPA_RX()
        {
            NADR = 0x0000;              // Reset Node address
            PNUM = 0x00;                // Reset peripheral number
            PCMD = 0x00;                // Reset peripheral command
            HWPID = 0xFFFF;             // All HWPIDs
            Data = new byte[55];        // New DPA data array
            DLEN = 0;                   // Reset Data length
            ErrN = 0;
            DpaValue = 0;
            

            CRC = 0x00;                 // Reset CRC          
            Buffer = new ArrayList();
        }


        // This method try to parse DPA message against incomming character
        public DPA_RX_STATE DPA_RX_Parse(byte character)
        {
            DPA_RX_STATE ret_val = DPA_RX_STATE.DPA_RX_NOERR;

            if (character == HDLC_FLAG_SEQUENCE)        // flag sequence
            {
                // first Flag sequnce
                if (Buffer.Count == 0)
                {
                    Buffer.Add((byte)character);
                    HDLC_CE = false;
                }
                else
                {
                    // It is error state - too short message
                    if (Buffer.Count < (HDLC_MIN_LEN-1))
                    {
                        // Maybe it is start of new frame...
                        Buffer.Clear(); Buffer.Add(character);
                        return DPA_RX_STATE.DPA_RX_FE;
                    }
                    // Correct length
                    else
                    {
                        // Check CRC                        
                        Buffer.RemoveAt(0); // remove first Flag sequnce                       
                        byte crc = DPA_UTILS.CalcCRC(Buffer);
                        // CRC is OK
                        if (crc == 0)
                        {
                            byte[] tmpBuffer = new byte[Buffer.Count];
                            Buffer.CopyTo(tmpBuffer);                   
                            NADR = tmpBuffer[1]; 
                            NADR = (UInt16)(NADR<<8);          // NADH.high8
                            NADR |= tmpBuffer[0];              // NADR.low8
                            PNUM = tmpBuffer[2];               // PNUM
                            PCMD = tmpBuffer[3];               // PCMD
                            HWPID = tmpBuffer[5]; 
                            HWPID = (UInt16)(HWPID << 8);       // HWPID.high8
                            HWPID |= tmpBuffer[4];              // HWPID.low8                            
                            ErrN = tmpBuffer[6];
                            DpaValue = tmpBuffer[7];
                            CRC = tmpBuffer[8];
                            Buffer.Clear(); 
                            return DPA_RX_STATE.DPA_RX_OK;
                        }
                        // CRC is no OK
                        else
                        {
                            // Maybe it is start of new frame...
                            Buffer.Clear(); Buffer.Add((byte)0x7E);
                            return DPA_RX_STATE.DPA_RX_CRCERR;
                        }
                    }
                }

            }
            else // if another character received
            {
                // if it is not the first character and length is within borders
                if ((Buffer.Count > 0) && (Buffer.Count < HDLC_MAX_LEN))
                {
                    // if Control Esape received
                    if (character == HDLC_CONTROL_ESCAPE)
                        HDLC_CE = true;
                    else
                    {   // else insert character
                        if (HDLC_CE == false)
                            Buffer.Add((byte)character);
                        else
                        {
                            HDLC_CE = false;
                            Buffer.Add((byte)character ^ (byte)HDLC_ESCAPE_BIT);
                        }
                    }
                }
            }

            return ret_val;
        }

    }

    ///<summary>
    ///DPA TX class
    ///</summary>
    ///<remarks>
    ///This class handles TX performance of DPA Protol
    ///</remarks>
    class DPA_TX
    {
        public UInt16 NADR;             // Node address
        public byte PNUM;               // Peripheral number
        public byte PCMD;               // Peripheral command
        public UInt16 HWPID;            // Hardware profile ID
        public byte[] Data;             // DPA Data
        public byte DLEN;               // DPA Data length
        
        private byte CRC;               // HDLC CRC
        public byte[] Buffer;           // Output buffer

        // Constructor
        public DPA_TX()
        {
            NADR = 0x0000;              // Reset Node address
            PNUM = 0x00;                // Reset peripheral number
            PCMD = 0x00;                // Reset peripheral command
            HWPID = 0xFFFF;             // All HWPIDs
            Data = new byte[55];        // New DPA data array
            DLEN = 0;                   // Reset Data length

            CRC = 0x00;                 // Reset CRC            
        }
        
        // This method fill compile DPA message to HDLC
        public void BuildHDLC()
        {
            byte temp;
            ArrayList tmpBuffer = new ArrayList();
            ArrayList tmpBuffer2 = new ArrayList();

            // Clear buffer
            tmpBuffer.Clear();
            
            // Add NADR
            temp = (byte)NADR;
            tmpBuffer.Add(temp);
            temp = (byte)(NADR >> 8);
            tmpBuffer.Add(temp);

            // Add PNUM
            tmpBuffer.Add(PNUM);

            // Add PCMD
            tmpBuffer.Add(PCMD);

            // Add HWPID
            temp = (byte)HWPID;
            tmpBuffer.Add(temp);
            temp = (byte)(HWPID >> 8);
            tmpBuffer.Add(temp);

            // Add Data
            for (byte i = 0; i < DLEN; i++)
                tmpBuffer.Add(Data[i]);

            // Add CRC
            temp = DPA_UTILS.CalcCRC(tmpBuffer);
            tmpBuffer.Add(temp);

            // Make a HDLC frame
            tmpBuffer2.Clear();
            tmpBuffer2.Add((byte)0x7E);    // Flag sequence
            foreach (byte tmp in tmpBuffer)
            {
                temp = tmp;
                // If there is Flag sequence or Control escape
                if ((temp == (byte)0x7D) || (temp == (byte)0x7E))
                {
                    tmpBuffer2.Add((byte)0x7D);
                    tmpBuffer2.Add((byte)(temp ^ 0x20));
                }
                else
                {
                    tmpBuffer2.Add((byte)temp);
                }
            }
            tmpBuffer2.Add((byte)0x7E);    // Flag sequence

            // Copy result to Buffer
            Buffer = new byte[tmpBuffer2.Count];
            tmpBuffer2.CopyTo(Buffer);
        }        

    }


    ///<summary>
    ///DPA UTILS class
    ///</summary>
    ///<remarks>
    ///This class helps with CRC and many other things in future
    ///</remarks>
    class DPA_UTILS
    {

        // return IQRF DPA CRC
        public static byte CalcCRC(ArrayList buffer)
        {
            byte crc = 0xFF;

            foreach (byte val in buffer)
            {
                byte value = val;
                for (int bitLoop = 8; bitLoop != 0; --bitLoop, value >>= 1)
                    if (((crc ^ value) & 0x01) != 0)
                        crc = (byte)((crc >> 1) ^ 0x8C);
                    else
                        crc >>= 1;
            }
            return crc;
        }

    }
}
