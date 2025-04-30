# type: ignore
# ruff: noqa
import numpy as np
from fractions import Fraction


def generate_shamir_example(secret, t, n, a_coeffs=None):
    """
    生成一个Shamir秘密共享的例子并输出LaTeX代码

    参数:
        secret: 需要共享的秘密整数
        t: 恢复秘密所需的最小分片数
        n: 总分片数
        a_coeffs: 多项式系数（可选）
    """
    # 如果未提供系数，则随机生成
    if a_coeffs is None:
        a_coeffs = [np.random.randint(1, 100) for _ in range(t - 1)]

    # 确保a_coeffs长度正确
    assert len(a_coeffs) == t - 1, f"系数长度应为 {t - 1}"

    # 构建多项式 f(x) = secret + a_1*x + a_2*x^2 + ... + a_{t-1}*x^{t-1}
    all_coeffs = [secret] + a_coeffs

    # 计算每个参与者的分片
    shares = []
    for i in range(1, n + 1):
        y = sum(all_coeffs[j] * (i**j) for j in range(t))
        shares.append((i, y))

    # 选择t个分片进行恢复
    selected_shares = shares[:t]

    # LaTeX输出
    latex_output = generate_latex(secret, t, n, all_coeffs, shares, selected_shares)

    return {
        "secret": secret,
        "polynomial": all_coeffs,
        "shares": shares,
        "selected_shares": selected_shares,
        "latex": latex_output,
    }


def lagrange_interpolation(points, x_value=0):
    """使用Lagrange插值法恢复秘密"""
    result = 0
    x_points, y_points = zip(*points)

    # 计算每个点的拉格朗日基本多项式值并相加
    for i in range(len(points)):
        term = y_points[i]
        for j in range(len(points)):
            if i != j:
                term *= Fraction(x_value - x_points[j], x_points[i] - x_points[j])
        result += term

    return result


def generate_latex(secret, t, n, coeffs, shares, selected_shares):
    """生成完整的LaTeX代码"""
    # 构建多项式字符串
    poly_str = f"{coeffs[0]}"
    for i in range(1, len(coeffs)):
        if coeffs[i] > 0:
            poly_str += f" + {coeffs[i]}"
        else:
            poly_str += f" - {abs(coeffs[i])}"

        if i == 1:
            poly_str += "x"
        else:
            poly_str += f"x^{i}"

    # 计算拉格朗日插值步骤
    lagrange_steps = []
    result = 0
    for i, (x_i, y_i) in enumerate(selected_shares):
        term = y_i
        term_str = f"{y_i}"

        for j, (x_j, _) in enumerate(selected_shares):
            if i != j:
                fraction = Fraction(0 - x_j, x_i - x_j)
                term *= fraction

                # 构建拉格朗日基本多项式的LaTeX表示
                term_str += f"\\cdot\\frac{{0-{x_j}}}{{{x_i}-{x_j}}}"

        # 添加简化步骤
        simplified_term = int(term) if term.denominator == 1 else term
        lagrange_steps.append((term_str, simplified_term))
        result += simplified_term

    # 生成最终的LaTeX代码
    latex = f"""
举例说明：假设我们有一个秘密数字$S={secret}$，我们希望将其分割成{n}个片段，
但只需要{t}个片段就可以恢复它（即$t={t},n={n}$）：
选择一个{t - 1}次多项式（因为$t-1={t - 1}$）:
\\[f(x) = """

    # 添加多项式表达式
    for i in range(t):
        if i == 0:
            latex += f"a_{i}"
        else:
            latex += f" + a_{i}x^{i}"
    latex += "\\]\n"

    # 添加具体的多项式
    latex += f"假设我们选择"
    for i in range(1, t):
        if i < t - 1:
            latex += f"$a_{i}={coeffs[i]}$, "
        else:
            latex += f"$a_{i}={coeffs[i]}$"
    latex += f"，那么多项式就是：\n\\[f(x) = {poly_str}\\]\n"

    # 添加分片计算
    latex += "为每个参与者选择一个$x$值并计算$f(x)$：\n"
    for x, y in shares:
        latex += f"\\[f({x}) = {' + '.join([f'{coeffs[i]}\\cdot{x}^{i}' if i > 0 else f'{coeffs[i]}' for i in range(t)])} = {y}\\]\n"

    # 添加分片分配
    share_str = ", ".join([f"$({x},{y})$" for x, y in shares])
    latex += f"每个参与者分别得到一个片段：{share_str}。\n"

    # 添加恢复秘密的说明
    latex += f"要恢复秘密，我们可以选择其中任意{t}个片段。\n"
    selected_str = "和".join([f"$({x},{y})$" for x, y in selected_shares])
    latex += f"假设我们选择{selected_str}，使用Lagrange插值可以计算出$f(0)={secret}$，从而恢复秘密。\n"

    # 添加拉格朗日插值公式
    latex += "具体的Lagrange插值公式为：\n"
    latex += "\\[f(x) = \\sum_{i=1}^t y_i \\prod_{j=1,j\\neq i}^t \\frac{x-x_j}{x_i-x_j}\\]\n"

    # 添加具体的拉格朗日插值计算
    latex += f"在这个例子中，使用{selected_str}进行插值：\n"
    terms = []
    calculations = []

    for term_str, simplified_term in lagrange_steps:
        terms.append(term_str)
        calculations.append(str(simplified_term))

    latex += (
        f"\\[f(0) = {' + '.join(terms)} = {' + '.join(calculations)} = {result}\\]\n"
    )
    latex += f"这就恢复出了原始的秘密值{secret}。"

    return latex


if __name__ == "__main__":
    # 设置的参数
    my_secret = 89  # 秘密数字
    threshold = 2  # 恢复秘密所需的最小分片数
    total_shares = 4  # 总分片数
    coefficients = [23]  # 多项式系数 (除了常数项外，t-1个系数)

    # 生成例子
    example = generate_shamir_example(my_secret, threshold, total_shares, coefficients)

    # 打印LaTeX代码
    print(example["latex"])

    # 验证秘密恢复是否正确
    recovered_secret = lagrange_interpolation(example["selected_shares"])
    assert recovered_secret == my_secret, "恢复的秘密不正确！"
