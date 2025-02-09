import sys
import importlib
import time


def run_test(test_name):
    module_name = f"tests.test_{test_name}"
    errors = []

    try:
        # 导入指定模块
        module = importlib.import_module(module_name)

        # 获取test_main方法
        test_main = getattr(module, "test_main")

        # 输出开始运行的时间和测试名
        print(f"时间：{time.strftime('%Y-%m-%d %H:%M:%S')} - start run {test_name}")

        # 调用test_main方法
        test_main()
    except ModuleNotFoundError:
        error_message = f"Module '{module_name}' not found."
        errors.append(error_message)
    except AttributeError:
        error_message = f"Method 'test_main' not found in module '{module_name}'."
        errors.append(error_message)
    except Exception as e:
        error_message = f"Error running test_main in module '{module_name}': {e}"
        errors.append(error_message)

    return errors


def main():
    # 检查参数数量
    if len(sys.argv) < 2:
        print("Usage: python test.py <test_name1> <test_name2> ...")
        sys.exit(1)

    # 提取参数值（从第一个参数开始）
    test_names = sys.argv[1:]

    # 用于存储所有错误
    all_errors = []

    # 逐个运行测试
    for test_name in test_names:
        errors = run_test(test_name)
        all_errors.extend(errors)

    # 输出所有出错的信息
    if all_errors:
        print("\nAll errors:")
        for error in all_errors:
            print(error)


if __name__ == "__main__":
    main()
