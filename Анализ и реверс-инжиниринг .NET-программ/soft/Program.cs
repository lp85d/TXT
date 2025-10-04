using System;
using System.IO;
using dnlib.DotNet;
using dnlib.DotNet.Emit;

namespace PatchLaitis {
    class Program {
        static void Main(string[] args) {
            string inputPath = @"C:\Program Files (x86)\Laitis\Laitis.exe";
            string outputPath = @"C:\Users\user\Downloads\PatchLaitis\LaitisPatched.exe";

            Console.WriteLine("Загружаем Laitis.exe...");
            ModuleDefMD module = ModuleDefMD.Load(inputPath);

            int patched = 0;

            foreach (var type in module.Types) {
                switch (type.Name) {
                    case "wKA":
                        Patch_wKA(type, ref patched);
                        break;
                    case "Bi":
                        Patch_Bi(type, ref patched);
                        break;
                    case "Aj":
                        Patch_Aj(type, ref patched);
                        break;
                    case "3Q":
                        Patch_3Q(type, ref patched);
                        break;
                    case "On":
                        Patch_On(type, ref patched);
                        break;
                    case "pCA":
                        Patch_pCA(type, ref patched);
                        break;
                }
            }

            Console.WriteLine($"Пропатчено методов: {patched}");
            Console.WriteLine("Сохраняем новый exe...");
            module.Write(outputPath);
            Console.WriteLine("✅ Готово! Новый файл: " + outputPath);
        }

        // ================= PATCH HELPERS =================
        static void ReplaceWithReturnString(MethodDef method, string value) {
            method.Body = new CilBody();
            method.Body.Instructions.Add(OpCodes.Ldstr.ToInstruction(value));
            method.Body.Instructions.Add(OpCodes.Ret.ToInstruction());
        }

        static void ReplaceWithReturnNull(MethodDef method) {
            method.Body = new CilBody();
            method.Body.Instructions.Add(OpCodes.Ldnull.ToInstruction());
            method.Body.Instructions.Add(OpCodes.Ret.ToInstruction());
        }

        static void ReplaceWithReturnBool(MethodDef method, bool val) {
            method.Body = new CilBody();
            method.Body.Instructions.Add((val ? OpCodes.Ldc_I4_1 : OpCodes.Ldc_I4_0).ToInstruction());
            method.Body.Instructions.Add(OpCodes.Ret.ToInstruction());
        }

        static void ReplaceWithReturnVoid(MethodDef method) {
            method.Body = new CilBody();
            method.Body.Instructions.Add(OpCodes.Ret.ToInstruction());
        }

        // ================= PATCH CLASSES =================
        static void Patch_wKA(TypeDef type, ref int patched) {
            foreach (var m in type.Methods) {
                if (!m.HasBody) continue;

                if (m.Name.Contains("DownloadString") || m.Name.Contains("getUpdates")) {
                    ReplaceWithReturnString(m, "{}"); patched++;
                }
                else if (m.Name.Contains("UploadString") || m.Name.Contains("publish")) {
                    ReplaceWithReturnString(m, "ok"); patched++;
                }
                else if (m.Name.Contains("SendStatistics")) {
                    ReplaceWithReturnVoid(m); patched++;
                }
                else if (m.Name.Contains("AuthorizationResponse")) {
                    ReplaceWithReturnNull(m); patched++;
                }
            }
        }

        static void Patch_Bi(TypeDef type, ref int patched) {
            foreach (var m in type.Methods) {
                if (m.Name.Contains("UploadDump")) {
                    ReplaceWithReturnVoid(m); patched++;
                }
            }
        }

        static void Patch_Aj(TypeDef type, ref int patched) {
            foreach (var m in type.Methods) {
                if (m.Name.Contains("GetToken") || m.Name.Contains("Azure")) {
                    ReplaceWithReturnString(m, "fake-token"); patched++;
                }
            }
        }

        static void Patch_3Q(TypeDef type, ref int patched) {
            foreach (var m in type.Methods) {
                if (m.Name.Contains("getUpdates") || m.Name.Contains("DownloadFile")) {
                    ReplaceWithReturnVoid(m); patched++;
                }
            }
        }

        static void Patch_On(TypeDef type, ref int patched) {
            foreach (var m in type.Methods) {
                if (m.Name.Contains("DownloadFile") || m.Name.Contains("TaskAsync")) {
                    ReplaceWithReturnVoid(m); patched++;
                }
            }
        }

        static void Patch_pCA(TypeDef type, ref int patched) {
            foreach (var m in type.Methods) {
                if (m.Name.Contains("RCA") || m.Name.Contains("sCA") || m.Name.Contains("Create")) {
                    ReplaceWithReturnNull(m); patched++;
                }
            }
        }
    }
}
